"""
Jupyter Environment.

Our local context was an "Introduction to Computational Thinking" course. We incorporated a special
toolbar that hid some features and exposed a new "run all" button that ran the students code and then
also a special cell at the end which grabbed the students' code.

Adds in two special magic commands when integrated into a Jupyter environment:
    %grade
    %grade_blockpy

If you want to use this, we expect there to be some work involved. We haven't really made it portable
and extensible the way we have everything else, because we aren't sure if anyone would want to use it.
We really need someone with a dedicated interest to shepard it.

"""

# Built-in imports
import json
import requests

# IPython imports
from IPython.core.magic import (Magics, magics_class, line_magic, cell_magic, line_cell_magic)
from IPython.display import Javascript, display
from IPython.utils.io import capture_output, CapturedIO

# Logging imports
import os
import sys
from warnings import warn
# from traitlets import Bool
import time

# TODO: Opportunity here to add in requests-cache. This would allow us to avoid
# the repeated trip. However, you'll need to handle expiring the cache in a
# smart way. One option is to write a command line script to just wipe as
# necessary. Simply deleting the cache file would be pretty easy, assuming it
# installs per user.

# TODO: MAKE THIS A CONFIG SETTING
BLOCKPY_URL = 'https://think.cs.vt.edu/blockpy/blockpy/load_assignment_give_feedback'


def get_response_error(response):
    """
    Transform a Response object into a friendlier string.

    Args:
        response (requests.Response): A Requests reponse object to parse for
                                      some kind of error.
    Returns:
        str: A string representation of the URL response.
    """
    return "{} {}: {}".format(response.status_code, response.reason,
                              response.text)


def download_on_run(assignment_id):
    """
    Download the on_run (give_feedback) code to use to test their solution.

    Args:
        assignment_id (int OR str): The ID of the assignment to get the
                                    on_run code for.
    Returns:
        bool: Whether or not the request was successful.
        str: If unsuccesful, a message to display to the user. Otherwise, it'll
             be the on_run code.
    """
    data = {'assignment_id': assignment_id}
    try:
        response = requests.get(BLOCKPY_URL, data=data)
    except Exception as error:
        return False, str(error)
    try:
        result = response.json()
    except ValueError:
        # Failed to parse the JSON; perhaps it was some text data?
        return False, get_response_error(response)
    if result['success']:
        return True, result['give_feedback']
    else:
        return False, result['message']


PEDAL_PIPELINE = '''
from pedal.core.report import MAIN_REPORT
MAIN_REPORT.clear()

# Load in some commonly used tools
from pedal.cait.cait_api import parse_program
from pedal.sandbox.commands import *
from pedal.core.commands import *

from pedal.environments.blockpy import setup_environment
# Initialize the BlockPy environment
pedal = setup_environment(skip_tifa=False,
                          skip_run=False,
                          inputs={inputs},
                          main_file='answer.py',
                          main_code={student_code})
student = pedal.fields['student']

{on_run}

from pedal.resolvers.simple import resolve
final = resolve()
SUCCESS = final.success
SCORE = final.score
CATEGORY = final.category
LABEL = final.title
MESSAGE = final.message
DATA = final.data
HIDE = final.hide_correctness
'''


def blockpy_grade(assignment_id, student_code, inputs):
    """
    Helper function to capture the request from the server.

    Args:
        assignment_id (int): The assignment ID to look up and use the on_run
                             code for.
        student_code (str): The code that was written by the student.

        inputs (str): The inputs to queue into the assignment

    Returns:
        str: The HTML formatted feedback for the student.
    """
    successful_download, on_run = download_on_run(assignment_id)
    # If it failed, let's display some information about why.
    if not successful_download:
        return on_run
    return execute_on_run_code(on_run, student_code, inputs)


def execute_on_run_code(on_run, student_code, inputs):
    """
    Actually execute the on_run code for the given student code.
    """
    # Even though the student code is a string, we need to escape it to prevent
    # any weirdness from being in the instructor code.
    escaped_student_code = json.dumps(student_code)
    instructor_code = PEDAL_PIPELINE.format(on_run=on_run,
                                            student_code=escaped_student_code,
                                            # inputs=','.join(inputs))
                                            inputs=inputs)
    # Execute the instructor code in a new environment
    global_variables = globals()
    compiled_code = compile(instructor_code, 'instructor_code.py', 'exec')
    exec(compiled_code, global_variables)
    category = global_variables['CATEGORY']
    label = global_variables['LABEL']
    message = global_variables['MESSAGE']
    # In some cases, we might want to override how the text is rendered.
    if category.lower() == 'instructor' and label.lower() == 'explain':
        category = "Instructor Feedback"
        label = ''
    # Return the result as HTML
    return '''<strong>{}</strong>: {}<br>{}'''.format(category, label, message)


# The following string literals are used to create the JavaScript code that
# creates the Python code that will execute the instructor's feedback code
# using the student's Python code.

# Extract out the student code, embed the result
EXTRACT_STUDENT_CODE = r"""
// Convert Notebook cells to a string of Python code
var makePython = function(cell) {
    if (cell.cell_type == "code") {
        // Code is embedded unchanged, unless it is magic
        var source = cell.get_text();
        if (source.startsWith('%')) {
            // Skip magic
            return '';
        } else {
            return source;
        }
    } else if (cell.cell_type == "markdown" ||
               cell.cell_type == "raw") {
        // Markdown and text is wrapped in a string.
        var escaped_text = cell.get_text().replace(/'''/g, "\\'\\'\\'");
        return "'''"+escaped_text+"'''";
    }
}
var isUsable = function(cell) {
    return cell.cell_type == "code" ||
           cell.cell_type == "markdown" ||
           cell.cell_type == "raw";
}
var cells = Jupyter.notebook.get_cells();
var source_code = cells.filter(isUsable).map(makePython).join("\n");
source_code = JSON.stringify(source_code);
console.log(source_code);
// Start constructing the feedback code (which will be Python).
var on_run_code = [];
on_run_code.push("student_code="+source_code);
"""

# Retrieve the last cell, and also recolor it a little for style
ANIMATE_LAST_CELL = r"""
// While we are accessing the server, recolor the last cell a little.
var last = null;
if (cells.length > 0) {
    last = cells[cells.length-1];
    $(last.element).animate({"background-color": "#E0E6FF"}, 1000);
}
"""

# If the %grade magic is used, we run the code directly.
LOCAL_GRADE = r'''
on_run_code.push("from pedal.environments.jupyter import execute_on_run_code");
on_run_code.push('print(execute_on_run_code({on_run_code}, student_code, {inputs}))');
'''

# If the %grade_blockpy magic is used, we need to get the on_run from blockpy.
BLOCKPY_GRADE = r'''
on_run_code.push("from pedal.environments.jupyter import blockpy_grade");
on_run_code.push('import json')
on_run_code.push('inputs = {inputs}')
console.log('inputs = {inputs}')
on_run_code.push("print(blockpy_grade({assignment}, student_code, inputs))");
'''

# This chunk actually performs the on_run code execution using the kernel.
EXECUTE_CODE = r'''
on_run_code = on_run_code.join("\n");
console.log(on_run_code);
var kernel = IPython.notebook.kernel;
if (kernel !== null) {
    var t = kernel.execute(on_run_code, { 'iopub' : {'output' : function(x) {
        if (x.msg_type == "error") {
            // If this was an error, show the traceback properly.
            if (last !== null) {
                last.output_area.append_error(x.content);
                console.error(x);
            } else {
                console.error("Could not append to final cell.", x);
            }
        } else if (!x.content.data && x.content.text) {
            // If it was valid data, we show it as HTML.
            console.log(x);
            element.html(x.content.text.replace(/\n/g, "<br>"));
        } else {
            // I'm not sure what it is - better dump it on the console.
            console.log(x);
        }
        // Decolor the last cell if it was there.
        if (last !== null) {
            last = cells[cells.length-1];
            $(last.element).animate({"background-color": "white"}, 1000);
        }
    }}});
}'''


@magics_class
class GradeMagic(Magics):
    """
    This class holds the magic for the %grade and %grade_blockpy
    """

    @line_magic
    def grade_logstart(self, line=""):
        """

        Args:
            line:
        """
        # ######Logging
        ts = time.time()
        logger = self.shell.logger  # logging
        old_logfile = self.shell.logfile  # logging
        directory = os.path.expanduser("log_folder{}~/".format(line))
        logfname = os.path.expanduser("log_folder{}~/log_{}.py~".format(line, ts))
        self.shell.logfile = logfname
        loghead = u'# IPython log file\n\n'
        try:
            os.makedirs(directory, exist_ok=True)
            logger.logstart(logfname, loghead, 'rotate', True, True,
                            True)
        except BaseException:
            self.shell.logfile = old_logfile
            warn("Couldn't start log: %s" % sys.exc_info()[1])
        self.shell.run_code("input = __builtins__.input")
        self.shell.run_code("print = __builtins__.print")
        self.shell.run_code("sum = __builtins__.sum")
        self.shell.run_code("len = __builtins__.len")

    @line_magic
    def grade_logstop(self, line=""):
        """

        Args:
            line:
        """
        self.shell.logger.logstop()

    def logging(self):
        """

        """
        # ######Logging
        ts = time.time()
        logger = self.shell.logger  # logging
        old_logfile = self.shell.logfile  # logging
        """
        import subprocess
        p = subprocess.Popen("uname -n", stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()  # output contains the username
        """
        logfname = os.path.expanduser("log_folder~/log_{}.py~".format(ts))
        self.shell.logfile = logfname
        loghead = u'# IPython log file\n\n'
        try:
            logger.logstart(logfname, loghead, 'rotate', False, True,
                            True)
        except BaseException:
            self.shell.logfile = old_logfile
            warn("Couldn't start log: %s" % sys.exc_info()[1])
        logger.timestamp = False
        input_hist = self.shell.history_manager.input_hist_raw
        logger.log_write(u'\n'.join(input_hist[1:]))
        logger.log_write(u'\n')
        logger.timestamp = True
        self.shell.logger.logstop()
        # ######Logging

    # noinspection PyMethodMayBeStatic
    def grade_parser(self, line, cell=None):
        """

        Args:
            line:
            cell:

        Returns:

        """
        if ',' in line:
            if cell is None:
                assignment, line = line.split(",", maxsplit=1)
            else:
                assignment = None
            inputs = json.dumps(line.split(",")[1:])
            #inputs = "\\'" + inputs[1:len(inputs) - 1] + "\\'"
        else:
            if cell is None:
                assignment, inputs = line, ""
            else:
                inputs = line
                assignment = ""
            inputs = json.dumps(inputs.split(",")[1:])
        return {"inputs": inputs, "assignment": assignment}

    # noinspection PyMethodMayBeStatic
    def unified_helper(self, local_code, **kwargs):
        """

        Args:
            local_code:
            **kwargs:

        Returns:

        """
        code = EXTRACT_STUDENT_CODE
        code += ANIMATE_LAST_CELL
        code += local_code.format(**kwargs)
        code += EXECUTE_CODE
        return code

    @cell_magic
    def grade(self, line="", cell=""):
        """

        Args:
            line:
            cell:

        Returns:

        """
        dump = self.grade_parser(line, cell)
        code = self.unified_helper(LOCAL_GRADE, on_run_code="INSTRUCTOR_CODE", inputs=dump['inputs'])
        cell = cell.replace("\\", "\\\\")
        cell = cell.replace("\n", "\\n")
        cell = cell.replace("'", "\\'")
        cell = cell.replace('"', '\\"')
        # Runs this code in the kernel as python code
        # Can also run compiled code
        self.shell.run_code("INSTRUCTOR_CODE = " + '"' + cell + '"')
        # TODO: This was the easier way for me to get this to work
        #  This might be worth using in more depth to have less translation
        #  to and from javascript. See usage_examples
        return display(Javascript(code))

    @line_cell_magic
    def usage_examples(self, line="", cell="print('running cell')\nprint('running cell2')"):
        """

        Args:
            line:
            cell:
        """
        # Runs code in the kernel's context
        self.shell.run_code("print('fun')")

        # Runs code in kernel's context using compiled code
        sample = compile(cell, "usage_examples.py", "exec")
        self.shell.run_code(sample)

        # runs javascript code
        self.shell.run_cell_magic("javascript", "", "console.log('I do JAVASCRIPT');\n")
        # Maybe can use javascript execution to pass things around...not sure though...can't get it to work
        # You can pass values, but it doesn't seem to work unless you run it again.
        # https://michhar.github.io/javascript-and-python-have-a-party/

        self.shell.run_cell_magic(
            "javascript", "",
            # js_code = Javascript(
            """var callbacks = { iopub : { output: function(out_data){ console.log(out_data) } } };\n"""
            """var code = "fun = 12";\n"""
            """IPython.notebook.kernel.execute(code);\n""")
        # handle = display(js_code, display_id="usage_examples")
        # handle.update(handle)
        self.shell.run_cell_magic("javascript", "", "console.log('I do JAVASCRIPT TOO!!');\n")
        # captures standard output, standard error, etc. and stops or not stops it
        # class IPython.utils.capture.capture_output(stdout=True, stderr=True, display=True)
        # Note that Tracebacks aren't put in standard error?
        with capture_output(True, False, False) as captured:
            print(dir(self))
            self.shell.run_code("print(fun)")
            sys.stderr.write("spam\n")
        print("I captured stdout")
        print(captured.stdout)
        print("I captured stderr")
        print(captured.stderr)

    @line_magic
    def grade_blockpy(self, line=""):
        """

        Args:
            line:

        Returns:

        """
        dump = self.grade_parser(line)
        code = self.unified_helper(BLOCKPY_GRADE, assignment=dump["assignment"], inputs=dump["inputs"])
        return display(Javascript(code))


def load_ipython_extension(ipython):
    """
    Register this plugin with Jupyter Notebooks. Although it is allegedly
    necessary in order to make this a plugin, we do not actually use it.
    """
    ipython.register_magics(GradeMagic)

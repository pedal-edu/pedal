# Built-in imports
import json
from textwrap import indent
import requests

# IPython imports
from IPython.core.magic import (Magics, magics_class, line_magic, cell_magic)
from IPython.display import Javascript, display, HTML

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

# This really should come in as a configuration setting somewhere.
BLOCKPY_URL = 'https://think.cs.vt.edu/blockpy/load_assignment_give_feedback'


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
    except ValueError as error:
        # Failed to parse the JSON; perhaps it was some text data?
        return False, get_response_error(response)
    if result['success']:
        return True, result['give_feedback']
    else:
        return False, result['message']


PEDAL_PIPELINE = '''
from pedal.report import *
from pedal.report.imperative import *
clear_report()
from pedal.source import set_source
set_source({student_code})
from pedal.tifa import tifa_analysis
tifa_analysis(True)
from pedal.sandbox.compatibility import *
queue_input({inputs})
run_student(True)
student = get_sandbox()
from pedal.cait.cait_api import parse_program
{on_run}
from pedal.resolvers import simple
SUCCESS, SCORE, CATEGORY, LABEL, MESSAGE, DATA, HIDE = simple.resolve()
'''


def blockpy_grade(assignment_id, student_code, inputs):
    """
    Helper function to capture the request from the server.

    Args:
        assignment_id (int): The assignment ID to look up and use the on_run
                             code for.
        student_code (str): The code that was written by the student.

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
on_run_code.push("from pedal.plugins.grade_magic import execute_on_run_code");
on_run_code.push('print(execute_on_run_code({on_run_code}, student_code, {inputs}))');
'''

# If the %grade_blockpy magic is used, we need to get the on_run from blockpy.
BLOCKPY_GRADE = r'''
on_run_code.push("from pedal.plugins.grade_magic import blockpy_grade");
on_run_code.push('import json')
on_run_code.push('inputs = json.dumps({inputs})')
on_run_code.push("print(blockpy_grade({assignment}, student_code, inputs))");
'''

# This chunk actually performs the on_run code exeuction using the kernel.
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
        except:
            self.shell.logfile = old_logfile
            warn("Couldn't start log: %s" % sys.exc_info()[1])

    @line_magic
    def grade_logstop(self, line=""):
        self.shell.logger.logstop()
        self.shell.run_code("print = __builtins__.print")
        self.shell.run_code("input = __builtins__.input")
        self.shell.run_code("sum = __builtins__.sum")
        #self.shell.reset(new_session=False)

    def logging(self):
        # ######Logging
        ts = time.time()
        logger = self.shell.logger  # logging
        old_logfile = self.shell.logfile  # logging
        logfname = os.path.expanduser("log_folder~/log_{}.py~".format(ts))
        self.shell.logfile = logfname
        loghead = u'# IPython log file\n\n'
        try:
            logger.logstart(logfname, loghead, 'rotate', False, True,
                            True)
        except:
            self.shell.logfile = old_logfile
            warn("Couldn't start log: %s" % sys.exc_info()[1])
        logger.timestamp = False
        input_hist = self.shell.history_manager.input_hist_raw
        logger.log_write(u'\n'.join(input_hist[1:]))
        logger.log_write(u'\n')
        logger.timestamp = True
        self.shell.logger.logstop()
        # ######Logging

    @cell_magic
    def grade(self, line="", cell=""):
        # Concatenate the JS code and then execute it by displaying it
        code = EXTRACT_STUDENT_CODE
        code += ANIMATE_LAST_CELL
        code += LOCAL_GRADE.format(on_run_code=json.dumps(cell), inputs="''")
        code += EXECUTE_CODE
        # self.logging()
        return display(Javascript(code))

    @line_magic
    def grade_blockpy(self, line=""):
        if ',' in line:
            assignment, inputs = line.split(",", maxsplit=1)
        else:
            assignment, inputs = line, ""
        # Concatenate the JS code and then execute it by displaying it
        code = EXTRACT_STUDENT_CODE
        code += ANIMATE_LAST_CELL
        code += BLOCKPY_GRADE.format(assignment=assignment, 
                                     inputs=json.dumps(inputs))
        code += EXECUTE_CODE
        # self.logging()
        return display(Javascript(code))


def load_ipython_extension(ipython):
    """
    Register this plugin with Jupyter Notebooks. Although it is allegedly
    necessary in order to make this a plugin, we do not actually use it.
    """
    ipython.register_magics(GradeMagic)


"""    
DEPRECATED: The following lines of code do not seem to be necessary to
            register this plugin with Jupyter.
def _jupyter_server_extension_paths():
    return [{
        "module": "pedal.plugins.grade_magic"
    }]

# jupyter serverextension enable --py pedal.plugins.grade_magic
def load_jupyter_server_extension(nbapp):
    from IPython import get_ipython
    get_ipython().register_magics(GradeMagic)
"""
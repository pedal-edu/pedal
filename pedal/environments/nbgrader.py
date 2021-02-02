import re
import sys
import json
import unittest

from pedal import Submission
from pedal.core.final_feedback import FinalFeedback
from pedal.core.submission import create_ipynb_submission_parser
from pedal.resolvers.core import make_resolver
from pedal.source import verify, next_section as original_next_section
from pedal.core.feedback import Feedback
from pedal.core.environment import Environment
from pedal.core.report import MAIN_REPORT
from pedal.sandbox import run, get_sandbox, set_input, start_trace, get_output
from pedal.source.sections import FeedbackSourceSection
from pedal.tifa import tifa_analysis
from pedal.resolvers.simple import resolve as simple_resolve, by_priority
from pedal.core.formatting import Formatter, HtmlFormatter
from pedal.resolvers.silent import resolve as silent_resolve


def get_source_code():
    from pedal.environments.jupyter import EXTRACT_STUDENT_CODE, EXECUTE_CODE
    from IPython.display import display, HTML, Javascript
    from inspect import currentframe, getframeinfo
    import inspect
    from pprint import pprint
    frames = inspect.stack()
    for frame in frames:
        if frame.function == '<module>':
            break
    split_line = str(frame.lineno)
    get_source_code_js = Javascript("""
    console.log("HEY WAIT WHY");
    var output_area = this;
    // find my cell element
    var cell_element = output_area.element.parents('.cell');
    // which cell is it?
    var cells = Jupyter.notebook.get_cells();
    var cell_idx = Jupyter.notebook.get_cell_elements().index(cell_element);
    // TODO: Walk backwards to get last "Autograded Answer" cell
    // get the cell object
    let cell = null;
    for (let i= cell_idx; i > 0; i -= 1) {
        cell = Jupyter.notebook.get_cell(i);
        if (cell.metadata.nbgrader && cell.metadata.nbgrader.solution) {
            break;
        }
    }
    let instructor_cell = Jupyter.notebook.get_cell(cell_idx);
    let instructor_text = instructor_cell.get_text();
    instructor_text = instructor_text.split("\\n")
                                     .slice(""" + split_line + """)
                                     .join("\\n");
    console.log('>>>', instructor_text);
    let source_code = "";
    if (cell !== null) {{
        source_code = cell.get_text();
    }}

    var kernel = Jupyter.notebook.kernel;
    var get_source_code = "student_code="+JSON.stringify(source_code);
    get_source_code += `
from pedal.environments.nbgrader import NBGraderEnvironment
NBGraderEnvironment(main_code=student_code)
if True:
`+instructor_text;
    console.log(get_source_code);
    if (kernel !== null) {
        console.log("DOUBLE CHECK");
        console.log(kernel.execute(get_source_code, {
            iopub: {
                output: (data) => {
                    //console.log(">>>", data, output_area, instructor_cell);
                    if (data.msg_type !== "error" || data.content.ename !== "PedalNotebookException") {
                        output_area.handle_output(data);
                    } else {
                        console.error("Pedal Exception:", data);
                    }
                    /*
                    console.log('+++', data);
                    console.log(output_area);
                    console.log(cell_element);
                    console.log(instructor_cell);
                    data.output_type = data.msg_type;
                    instructor_cell.outputs.push(data);
                    if (data.msg_type == "error") {
                        // If this was an error, show the traceback properly.
                        output_area.append_error(data.content);
                        console.error(data);
                    } else if (data.msg_type === "display_data") {
                        // If it was valid data, we show it as HTML.
                        console.log(data);
                        output_area.append_display_data(data.content);
                        instructor_cell.outputs.push(data.content);
                        //output_area.element.html(output_area.element.html()+"\\n"+
                        //                         data.content.text.replace(/\\n/g, "<br>"));
                    } else {
                        // I'm not sure what it is - better dump it on the console.
                        console.log(data);
                    }
                */}
            }
        }));
    }
    console.log("FINISHED SETTING UP JS");
    """)

    # class UglyException(Exception):
    #    pass

    # def handle(*args, **kwargs):
    #    import ctypes
    #    frame = inspect.stack()[2].frame
    #    frame.f_locals['outflag'] = True
    #    ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(frame), ctypes.c_bool(True))

    # from IPython import get_ipython
    # get_ipython().set_custom_exc((UglyException,), handle)

    display(get_source_code_js)
    # import time
    # time.sleep(4)
    # raise UglyException()
    # print("FINISHED SET UP")
    return ""
    # return os.environ['STUDENT_SOURCE_CODE'] #student_code


from io import StringIO


class PedalNotebookException(SystemExit):
    """Exit Exception for IPython.

    Exception temporarily redirects stderr to buffer.
    """

    def __init__(self):
        # print("exiting")  # optionally print some message to stdout, too
        # ... or do other stuff before exit
        sys.stderr = StringIO()

    def __del__(self):
        sys.stderr.close()
        sys.stderr = sys.__stderr__  # restore from backup


def ipy_exit():
    raise PedalNotebookException


def in_notebook():
    """
    Returns ``True`` if the module is running in IPython kernel,
    ``False`` if in IPython shell or other Python shell.
    """
    from IPython import get_ipython
    return bool(get_ipython())
    # return 'ipykernel' in sys.modules #or 'IPython' in sys.modules


class NBGraderEnvironment(Environment):
    """
    Configures the NBGrader programming environment.
    """

    def __init__(self, files=None, main_file='answer.py', main_code=None,
                 user=None, assignment=None, course=None, execution=None,
                 instructor_file='on_run.py', skip_tifa=True, skip_run=True,
                 inputs=None, set_success=True,
                 report=MAIN_REPORT, trace=True):
        super().__init__(files=files, main_file=main_file, main_code=main_code,
                         user=user, assignment=assignment, course=course,
                         execution=execution, instructor_file=instructor_file,
                         report=report)
        # TODO: If WebCAT doesn't want HTML output, then we should switch the default formatter
        self.report.add_hook('pedal.report.add_feedback', self.force_immediate_errors)
        self.skip_run = skip_run
        self.skip_tifa = skip_tifa
        self.trace = trace
        report.set_formatter(Formatter(report))
        verify(report=self.report)
        if not skip_tifa:
            tifa_analysis(report=self.report)
        if inputs:
            set_input(inputs)
        if skip_run:
            student = get_sandbox(report=report)
        else:
            if trace:
                start_trace()
            student = run(report=report)
        self.fields = {
            'student': student,
            'resolve': silent_resolve,
        }

    def force_immediate_errors(self, feedback, report=None):
        if report is None:
            report = self.report
        if self.report.get_current_group() is not None:
            return False

        final = simple_resolve()
        tc = unittest.TestCase()
        with tc.subTest():
            tc.fail(final.message)

        # if in_notebook():
        #    from IPython.display import HTML, display
        #    display(HTML(f"""<strong>{final.title}</strong><br><div>{final.message}</div>"""))
        #    ipy_exit()
        # else:
        #    print(final.title, file=sys.stderr)
        #    print(final.message, file=sys.stderr)
        #    sys.exit(1)

    def load_main(self, path):
        """
        Allowed to return either a string value (the contents of the file)
        or the exception that was raised.
        """
        try:
            return super().load_main(path)
        except OSError as file_error:
            return file_error


def setup_environment(cells=None, **kwargs):
    """

    Args:
        cells: The subset of cells to get. Defaults to ALL cells (None, or '**'), including the non-solution cells.
            To limit to just solution cells, use '*'. You can also pass a single cell ID or a list of cell IDs
            to grab a specific subset of the notebook.
        ipynb_file:
        main_code:
        main_file:
        **kwargs:

    Returns:

    """
    if in_notebook():
        get_source_code()
        return False
    else:
        # Logic for parsing the `cells` parameter
        all_cells, all_solutions = False, False
        chosen_cells = []
        if cells is None or cells == '**':
            all_cells = True
        else:
            if isinstance(cells, str):
                chosen_cells.append(cells)
            else:
                chosen_cells.extend(cells)
            for cell in chosen_cells[:]:
                if cell == '*':
                    all_solutions = True
            # TODO: Support "<=" and ">=" to get adjacent cells?

        def metadata_filter(cell, other_cells) -> bool:
            if all_cells:
                return True
            nbgrader = cell.metadata.get('nbgrader', {})
            if all_solutions and nbgrader.get('solution', False):
                return True
            return nbgrader.get('grade_id') in chosen_cells

        Submission.PARSERS['ipynb'] = create_ipynb_submission_parser(metadata_filter)
        environment = NBGraderEnvironment(**kwargs)
        return environment

# # Old approach: inspecting the stack to get filename - yikes!
# import inspect
# student_filename = inspect.stack()[-1].filename
# with open(student_filename) as student_file:
#    main_code = student_file.read()

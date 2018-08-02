from IPython.core.magic import (Magics, magics_class, line_magic, cell_magic)
from IPython.display import Javascript, display, HTML
import json
from textwrap import indent

from requests import get

BLOCKPY_URL = 'https://think.cs.vt.edu/blockpy/'

def blockpy_grade(assignment_id, student_code):
    data = {'assignment_id': assignment_id}
    response = get(BLOCKPY_URL+'load_assignment_give_feedback', data=data)
    result = response.json()
    if result['success']:
        instructor_code = ('from pedal.report import *\n'+
                           'from pedal.report.imperative import *\n'+
                           'clear_report()\n'+
                           'from pedal.source import set_source\n'+
                           'set_source('+json.dumps(student_code)+')\n'+
                           'from pedal.sandbox.compatibility import *\n'+
                           'run_student()\n'+
                           'student = get_sandbox()\n'+
                           'from pedal.tifa import tifa_analysis\n'+
                           'tifa_analysis(True)\n'+
                           'from pedal.sandbox import compatibility\n'+
                           'student = compatibility.get_student_data()\n'+
                           'compatibility.run_student(True)\n'+
                           'from pedal.cait.cait_api import parse_program\n'+
                           result['give_feedback']+'\n'+
                           'from pedal.resolvers import simple\n'+
                           'SUCCESS, SCORE, CATEGORY, LABEL, MESSAGE, DATA, HIDE = simple.resolve()')
        gbls = {}
        exec(instructor_code, gbls, gbls)
        tb_if_any = ''#json.dumps(gbls['DATA'].get('sandbox', {}))
        display(HTML(gbls['CATEGORY']+'<br>'+
                     gbls['LABEL']+'<br>'+
                     gbls['MESSAGE']+'<br>'+
                     '<pre>{}</pre>'.format(tb_if_any)))
        return ('<strong>'+gbls['CATEGORY']+'</strong>: '+
                     gbls['LABEL']+'<br>'+
                     gbls['MESSAGE']+'<br>')
    else:
        return ""


EMBED_STUDENT_CODE = r'''
var cells = Jupyter.notebook.get_cells();
if (cells.length > 0) {
    var last = cells[cells.length-1];
    $(last.element).animate({"background-color": "#F6FAFF"}, 1000);
}
var source_code = Jupyter.notebook.get_cells().map(function(cell) {
    if (cell.cell_type == "code") {
        var source = cell.code_mirror.getValue();
        if (!source.startsWith("%")) {
            return source;
        }
    }
}).join("\n");
source_code = JSON.stringify(source_code);
var instructor_code = "student_code="+source_code+"\n";
'''
LOCAL_GRADE = r'''instructor_code += {code}
console.log(instructor_code);'''
BLOCKPY_GRADE = r'''//instructor_code += "\nimport ast\nprint(ast.dump(ast.parse(student_code)))\nprint('Great')"
instructor_code += "from pedal.plugins.grade_magic import blockpy_grade\n";
instructor_code += "result=blockpy_grade({assignment}, student_code);\n"
instructor_code += "print(result)\n"
console.log(instructor_code);'''
EXECUTE_CODE = r'''
var kernel = IPython.notebook.kernel;
if (kernel !== null) {
    var t = kernel.execute(instructor_code, { 'iopub' : {'output' : function(x) {
        if (x.msg_type == "error") {
            console.error(x);
            console.error(x.content);
            element.text(x.content.ename+": "+x.content.evalue+"\n"+x.content.traceback.join("\n"))
        } else if (!x.content.data && x.content.text) {
            console.log(x);
            element.html(x.content.text.replace(/\n/g, "<br>"));
            //console.log(x);
        } else {
            console.log(x);
        }
        if (cells.length > 0) {
            var last = cells[cells.length-1];
            $(last.element).animate({"background-color": "white"}, 1000);
        }
    }}});
}'''

@magics_class
class GradeMagic(Magics):
    @cell_magic
    def grade(self, line="", cell=""):
        code = EMBED_STUDENT_CODE
        code += LOCAL_GRADE.format(code=json.dumps(cell))
        code += EXECUTE_CODE
        return display(Javascript(code))
    @line_magic
    def grade_blockpy(self, line=""):
        code = EMBED_STUDENT_CODE
        code += BLOCKPY_GRADE.format(assignment=line)
        code += EXECUTE_CODE
        return display(Javascript(code))
        
def load_ipython_extension(ipython):
    ipython.register_magics(GradeMagic)

def load_jupyter_server_extension(nbapp):
    nbapp.register_magics(GradeMagic)

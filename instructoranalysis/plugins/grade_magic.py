from IPython.core.magic import (Magics, magics_class, line_magic, cell_magic)
from IPython.display import Javascript

GRADER_CODE = '''
var source_code = Jupyter.notebook.get_cells().map(function(cell) {{
    if (cell.cell_type == "code") {{
        var source = cell.code_mirror.getValue();
        if (!source.startsWith("%%")) {{
            return source;
        }}
    }}
}}).join("\n");
source_code = JSON.stringify(source_code);
var instructor_code = "student_code="+source_code;
instructor_code += "\nimport ast\nprint(ast.dump(ast.parse(student_code)))\nprint('Great')"
//instructor_code += "\nfrom instructor import blockpy_grade({assignment})"
console.log(instructor_code);
var kernel = IPython.notebook.kernel;
var t = kernel.execute(instructor_code, {{ 'iopub' : {{'output' : function(x) {{
    if (x.msg_type == "error") {{
        console.error(x.content);
        element.text(x.content.ename+": "+x.content.evalue+"\n"+x.content.traceback.join("\n"))
    }} else {{
        element.html(x.content.text.replace(/\n/g, "<br>"));
        //console.log(x);
    }}
}}}}}});'''

@magics_class
class GradeMagic(Magics):
    @line_magic
    def grade(self, line=""):
        return Javascript(GRADER_CODE.format(assignment=line)
        
def load_ipython_extension(ipython):
    ipython.register_magics(GradeMagic)
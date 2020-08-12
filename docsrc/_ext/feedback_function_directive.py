"""
Special Sphinx directive for documenting feedback functions.

"""


from importlib import import_module
from pprint import pformat
from docutils.parsers.rst import Directive
from docutils import nodes
from sphinx import addnodes

class FeedbackFunctionDirective(Directive):
    """Render a constant using pprint.pformat and insert into the document"""
    required_arguments = 1

    def run(self):
        module_path, member_name = self.arguments[0].rsplit('.', 1)

        member_data = getattr(import_module(module_path), member_name)
        code = pformat(member_data, 2, width=68)

        literal = nodes.literal_block(code, code)
        literal['language'] = 'python'

        title = (getattr(member_data, 'title', member_name) or
                 getattr(member_data, 'label', member_name) or "")
        justification = getattr(member_data, 'justification', "")
        muted = getattr(member_data, 'muted', False)
        if hasattr(member_data, 'message_template'):
            text = getattr(member_data, 'message_template')
        else:
            text = getattr(member_data, 'message')

        result = [addnodes.desc_classname(text="Feedback Function: "+title)]
        lst = nodes.bullet_list()
        item = nodes.list_item()
        lst += item
        item += nodes.strong(text="Label: ")
        item += nodes.inline(text=member_name)
        if muted:
            item = nodes.list_item()
            lst += item
            item += nodes.emphasis(text="Muted by default")
        item = nodes.list_item()
        lst += item
        item += nodes.strong(text="Justification: ")
        item += nodes.inline(text=justification)
        item = nodes.list_item()
        lst += item
        item += nodes.strong(text="Response: ")
        item += nodes.inline(text=text)
        result.extend([addnodes.desc_content('', lst)])

        return result


def setup(app):
    app.add_directive('feedback_function', FeedbackFunctionDirective)

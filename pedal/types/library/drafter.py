from pedal.types.new_types import ModuleType, FunctionType, void_function, ClassType, \
    InstanceType, bool_function, int_function, str_function, register_builtin_module, AnyType, ListType

# TODO: route, Button, ...

_VOID_FUNCTIONS = ['start_server', 'show_debug_information', 'hide_debug_information',
                   "deploy_site", "assert_equal", "set_website_framed",
                   "set_website_style", "set_website_title",
                   "add_website_header", "add_website_css"]
_COMPONENT_FUNCTIONS = ['Argument', 'Box', 'BulletedList', 'Button', 'CheckBox',
              'Div', 'Division', 'Download', 'FileUpload', 'Header',
              'HorizontalRule', 'Image', 'LineBreak', 'Link',
              'MatPlotLibPlot', 'NumberedList', 'PageContent', 'SubmitButton',
              'Pre', 'PreformattedText', 'Row', 'SelectBox', 'Span',
              'Table', 'Text', 'TextArea', 'TextBox']
_IDENTITY_FUNCTIONS = ["route", 'bold',
                       'change_background_color', 'change_border', 'change_color', 'change_height',
                       'change_margin', 'change_padding', 'change_text_align',
                       'change_text_decoration', 'change_text_font', 'change_text_size',
                       'change_text_transform', 'change_width', 'float_left', 'float_right',
                       'italic', 'large_font', 'monospace', 'small_font', 'strikethrough',
                       'underline', 'update_attr', 'update_style']

def build_drafter_module():
    _PageObject = ClassType('Page', {
        'state': AnyType(),
        'content': ListType(AnyType())
    }, [])

    def _PageObject_Constructor():
        return InstanceType(_PageObject)

    _ComponentObject = ClassType('Component', {}, [])

    def _ComponentObject_Constructor():
        return InstanceType(_ComponentObject)

    _DRAFTER_FIELDS = {
        'Page': FunctionType('Page', returns=_PageObject_Constructor),
        'get_server_setting': FunctionType('get_server_setting', returns=AnyType())
    }

    _DRAFTER_FIELDS.update({
        name: void_function(name) for name in _VOID_FUNCTIONS
    })
    _DRAFTER_FIELDS.update({
        name: FunctionType(name, returns=_ComponentObject_Constructor)
        for name in _COMPONENT_FUNCTIONS
    })
    _DRAFTER_FIELDS.update({
        name: FunctionType(name, returns='identity')
        for name in _IDENTITY_FUNCTIONS
    })
    return ModuleType('drafter', _DRAFTER_FIELDS, redefines={"assert_equal"})


register_builtin_module('drafter', build_drafter_module)

from pedal.types.new_types import ModuleType, FunctionType, void_function, ClassType, \
    InstanceType, bool_function, int_function, str_function, register_builtin_module, AnyType, ListType

# TODO: route, Button, ...

_VOID_FUNCTIONS = ['start_server', 'show_debug_information', 'hide_debug_information']
_COMPONENT_FUNCTIONS = ['BulletedList', 'Button', 'CheckBox',
                        'Header', 'HorizontalRule', 'Image', 'LineBreak', 'Link', 'LinkContent',
                        'NumberedList', 'PageContent', 'SelectBox',
                        'SubmitButton', 'Table', 'Text', 'TextArea', 'TextBox']
_IDENTITY_FUNCTIONS = ["route"]


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
    return ModuleType('drafter', _DRAFTER_FIELDS)


register_builtin_module('drafter', build_drafter_module)

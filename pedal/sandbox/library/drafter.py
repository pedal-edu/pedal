from pedal.sandbox.mocked import MockModule
from pedal.utilities.system import IS_PYTHON_36


class MockDrafter(MockModule):
    """
    This will eventually be much more sophisticated. We really need a "MockPygame" that provides a
    window-less version of itself suitable for testing. I think that will be very key for the long-term
    testing behavior of Designer!
    """
    UNKNOWN_FUNCTIONS = []

    SUBMODULES = []

    module_name = 'drafter'
    FIELDS = ['Any', 'BASELINE_ATTRS', 'BASIC_STYLE', 'Bottle', 'BulletedList', 'Button', 'CheckBox', 'ConversionRecord',
         'DEFAULT_BACKEND', 'Header', 'HorizontalRule', 'INCLUDE_STYLES', 'Image', 'LineBreak', 'Link', 'LinkContent',
         'MAIN_SERVER', 'NumberedList', 'Page', 'PageContent', 'RESTORABLE_STATE_KEY', 'SUBMIT_BUTTON_KEY', 'SelectBox',
         'Server', 'ServerConfiguration', 'SubmitButton', 'TEMPLATE_200', 'TEMPLATE_404', 'TEMPLATE_500', 'Table', 'Text',
         'TextArea', 'TextBox', 'URL_REGEX', 'VisitedPage', '_HtmlList', '__doc__', '__file__', '__name__', '__package__',
         '__version__', '_hijack_bottle', 'abort', 'asdict', 'bold', 'change_background_color', 'change_border',
         'change_color', 'change_height', 'change_margin', 'change_padding', 'change_text_align', 'change_text_decoration',
         'change_text_font', 'change_text_size', 'change_text_transform', 'change_width', 'check_invalid_external_url',
         'dataclass', 'dataclass_field', 'datetime', 'default_index', 'dehydrate_json', 'fields', 'float_left',
         'float_right', 'friendly_urls', 'hide_debug_information', 'inspect', 'is_dataclass', 'italic', 'json',
         'large_font', 'logger', 'logging', 'merge_url_query_params', 'monospace', 'parse_qs', 'pprint', 're',
         'rehydrate_json', 'remap_attr_styles', 'remove_url_query_params', 'replace', 'request', 'route',
         'show_debug_information', 'small_font', 'start_server', 'strikethrough', 'sys', 'traceback', 'underline',
         'update_attr', 'update_style', 'urlencode', 'urlparse', 'wraps']

    def __init__(self):
        super().__init__()
        self.calls = []

    def get_submodules(self):
        return {}

    def _reset_designer(self):
        self.calls = []

    def _generate_patches(self):
        if IS_PYTHON_36:
            # Generate patches manually
            return {name: self.getter(name) for name in self.FIELDS}
        else:
            return {'__getattr__': self.getter, '__all__': ['test']}

    def getter(self, key):
        """ If anything asks, we prevent the module. Except for __file__. """
        # Needed to support coverage - it's okay to ask who I am.
        if key == '__file__':
            return self.module_name
        if key == '__all__':
            return self.FIELDS

        def _fake_call_wrapper(*args, **kwargs):
            self.calls.append((key, args, kwargs))
            return self._fake_call(args, kwargs)

        return _fake_call_wrapper

    def _fake_call(self, *args, **kwargs):
        return 0



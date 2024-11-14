from dataclasses import dataclass
from pedal.sandbox.mocked import MockModuleExposing, MethodExposer
from pedal.sandbox.mocked import MockModule
from pedal.utilities.system import IS_PYTHON_36
from functools import wraps

try:
    import drafter
except:
    drafter = None


def friendly_urls(url: str) -> str:
    if url.strip("/") == "index":
        return "/"
    if not url.startswith('/'):
        url = '/' + url
    return url


@dataclass
class GenericComponent:
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs


def _load_drafter_component(name):

    @wraps(name)
    def call_drafter_component(*args, **kwargs):
        if drafter is not None:
            component = getattr(drafter, name)
            # Component Button <class 'drafter.Button'> (MockDrafter(), 'Change the Message', <function change_message>) {}
            # raise Exception(f"Component {name} {component} {args} {kwargs}")
            return component(*args[1:], **kwargs)
        else:
            return GenericComponent(name, *args, **kwargs)

    return call_drafter_component


class MockDrafter(MockModuleExposing):
    """
    Mock Drafter library that can be used to capture data from the students' program execution.
    """
    expose = MethodExposer()
    UNKNOWN_FUNCTIONS = [
              'abort', 'add_website_css', 'add_website_header', 'assert_equal', 'bold',
              'change_background_color', 'change_border', 'change_color', 'change_height', 'change_margin',
              'change_padding', 'change_text_align', 'change_text_decoration', 'change_text_font', 'change_text_size',
              'change_text_transform', 'change_width',
              'deploy_site', 'float_left', 'float_right',
              'get_server_setting', 'hide_debug_information',
              'italic', 'large_font', 'monospace',
              'set_website_framed', 'set_website_style', 'set_website_title',
              'show_debug_information', 'small_font', 'strikethrough',
              'underline', 'update_attr', 'update_style'
    ]


    def __init__(self):
        super().__init__()
        self.original_routes = []
        self.routes = {}
        self._unknown_calls = []
        self.server_started = False
        self.state = None

    def __repr__(self):
        return f"MockDrafter()"

    def __str__(self):
        return f"<MockDrafter()>"

    def add_route(self, url, func):
        self.original_routes.append((url, func))
        url = friendly_urls(url)
        self.routes[url] = func

    @expose
    def start_server(self, initial_state):
        self.server_started = True
        self.state = initial_state

    @expose
    def show_debug_information(self):
        pass

    @expose
    def hide_debug_information(self):
        pass

    @expose
    def route(self, url: str = None):
        if callable(url):
            local_url = url.__name__
            self.add_route(local_url, url)
            return url

        def make_route(func):
            local_url = url
            if url is None:
                local_url = func.__name__
            self.add_route(local_url, func)
            return func

        return make_route

COMPONENTS = ['Argument', 'Box', 'BulletedList', 'Button', 'CheckBox',
              'Div', 'Division', 'Download', 'FileUpload', 'Header',
              'HorizontalRule', 'Image', 'LineBreak', 'Link', 'LinkContent',
              'MatPlotLibPlot', 'NumberedList', 'PageContent',
              'Page',
              'Pre', 'PreformattedText', 'Row', 'SelectBox', 'Span',
              'SubmitButton',
              'Table', 'Text', 'TextArea', 'TextBox']

for component in COMPONENTS:
    loaded_component = _load_drafter_component(component)
    setattr(MockDrafter, component, loaded_component)
    MockDrafter.expose.add_with_name(loaded_component, component)



"""
route, start_server
'show_debug_information', 
'hide_debug_information',
'route', 'start_server',
         
         'bold', 'change_background_color', 'change_border',
         'change_color', 'change_height', 'change_margin', 'change_padding', 'change_text_align',
         'change_text_decoration',
         'change_text_font', 'change_text_size', 'change_text_transform', 'change_width',
         'float_left',
         'float_right',  
         'italic', 
         'large_font', 'monospace',
         'small_font', 'strikethrough', 'underline',
         'update_attr', 'update_style']
"""
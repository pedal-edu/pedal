"""
Helpful pages:

* Microbit library source code: https://github.com/bbcmicrobit/micropython/tree/master/source/microbit
* Microbit Python API typings: https://github.com/MrYsLab/pseudo-microbit/blob/master/microbit/__init__.py
"""

from pedal.sandbox.mocked import MockModule


def generic_function_capture(self, function_name):
    def _call(*args, **kwargs):
        """ This function does nothing. """
        # TODO: Capture name; does this need to be a decorated function?
        self._unknown_calls.append((function_name, args, kwargs))
    return _call


class MethodExposer:
    def __init__(self):
        self.tracked_functions = {}

    def __call__(self, function):
        self.tracked_functions[function.__name__] = function
        return function


class MockModuleExposing(MockModule):
    expose: MethodExposer
    UNKNOWN_FUNCTIONS: list

    def get_submodules(self):
        return {}

    def _generate_patches(self):
        # Use function descriptor to get a bound version of each method
        fields = {n: f.__get__(self) for n, f in self.expose.tracked_functions.items()}
        fields.update({
            name: generic_function_capture(self, name)
            for name in self.UNKNOWN_FUNCTIONS
        })
        fields.update(self.get_submodules())
        return fields


class MicrobitButton:
    is_pressed: bool
    was_pressed: bool
    presses: int

    def __init__(self):
        self.reset_state()

    def reset_state(self):
        self.is_pressed = False
        self.was_pressed = False
        self.presses = 0


class MicrobitDigitalPin:
    NO_PULL = 0
    PULL_UP = 1
    PULL_DOWN = 2

    value: float
    period: int

    def __init__(self):
        self.reset_state()

    def reset_state(self):
        self.value = 0
        self.period = 35


class MicrobitAnalogDigitalPin(MicrobitDigitalPin):
    pass


class MicrobitTouchPin(MicrobitAnalogDigitalPin):
    touched: bool

    def reset_state(self):
        super().reset_state()
        self.touched = False


class MicrobitDisplay:
    # Actual displayed data (`image_buffer` in c version)
    image: list  #: list[list[int]]
    # Other data
    previous_brightness: int
    active: bool
    strobe_row: int
    #: Histogram of brightnesses
    brightnesses: int
    #: Brightness level => # of pins
    pins_for_brightness: list  #: list[int]

    SIZE = 5

    def __init__(self):
        self.image = [[0 for _ in range(self.SIZE)] for _ in range(self.SIZE)]
        self.reset_state()

    def reset_state(self):
        for x in range(self.SIZE):
            for y in range(self.SIZE):
                self.image[x][y] = 0

    def copy(self):
        return [list(line) for line in self.image]


class MicrobitImage:
    pass


class MicrobitSimulator:
    #: Whether the board is in "panic mode" (error state)
    panic_mode: bool
    #: Status code of the microbit
    status_code: int
    #: Temperature in degrees celsius
    temperature: int
    #: Milliseconds since board started
    time: int

    button_a: MicrobitButton
    button_b: MicrobitButton

    pin0: MicrobitTouchPin
    pin1: MicrobitTouchPin
    pin3: MicrobitTouchPin
    # TODO: Finish these: https://github.com/MrYsLab/pseudo-microbit/blob/master/microbit/__init__.py#L159

    def __init__(self):
        self.button_a = MicrobitButton()
        self.button_b = MicrobitButton()
        self.pin0 = MicrobitTouchPin()
        self.pin1 = MicrobitTouchPin()
        self.pin2 = MicrobitTouchPin()
        self.reset_state()

    def reset_state(self):
        self.panic_mode = False
        self.status_code = 0
        self.temperature = 20
        self.time = 0
        self.button_a.reset_state()
        self.button_b.reset_state()
        self.pin0.reset_state()
        self.pin1.reset_state()
        self.pin2.reset_state()

    def __str__(self):
        if self.panic_mode:
            return "<MicrobitSimulator: PANIC MODE>"
        return "<MicrobitSimulator>"

    def __repr__(self):
        return f"MicrobitSimulator(panic_mode={self.panic_mode})"


class MockMicrobitDisplay(MockModuleExposing):
    """
    If needed, could make the history extremely compact by tracking changes instead, and storing
    them in a single integer. First 6 bits for the X/Y, and then 4 bits for the new value. Could also have some
    special codes, if needed (e.g., for "clear").
    """
    expose = MethodExposer()
    UNKNOWN_FUNCTIONS = []
    SUBMODULES = []
    DEFAULT_LIGHT_LEVEL = 110

    def __init__(self, display):
        super().__init__()
        self.light_level = self.DEFAULT_LIGHT_LEVEL
        self.history = []
        self.current = display
        self.clear()

    @expose
    def clear(self):
        self.light_level = self.DEFAULT_LIGHT_LEVEL
        self.current.reset_state()
        self.record_current()

    @expose
    def show(self, image, delay=400, wait=True, loop=False, clear=False):
        if isinstance(image, MicrobitImage):
            pass
        # TODO: Fix this to use the proper Image api!
        for y, row in enumerate(image):
            for x, brightness in enumerate(row):
                self.current.image[y][x] = brightness
        self.record_current()

    @expose
    def set_pixel(self, x, y, value):
        self.current.image[y][x] = value
        self.record_current()

    @expose
    def get_pixel(self, x, y):
        return self.current.image[y][x]

    def record_current(self):
        self.history.append(self.current.copy())

    @expose
    def read_light_level(self):
        return self.light_level

    @expose
    def set_light_level(self, light_level):
        self.light_level = light_level


class MockMicrobit(MockModuleExposing):
    """
    Mock Microbit library that can be used to capture data from the students' program execution.
    """
    expose = MethodExposer()
    UNKNOWN_FUNCTIONS = []

    SUBMODULES = [
        'microbit.display'
    ]

    def __init__(self):
        super().__init__()
        self.state = MicrobitSimulator()
        self.display = MockMicrobitDisplay(MicrobitDisplay())
        self._unknown_calls = []

    def __repr__(self):
        return f"MockMicrobit(_state={self._state!r})"

    def __str__(self):
        return f"<MockMicrobit ({self._state!r})>"


    @expose
    def panic(self, n: int = 999):
        self.state.panic_mode = True
        self.state.status_code = n

    @expose
    def reset(self):
        self.state.reset_state()

    @expose
    def sleep(self, n: float):
        self.state.time += n

    @expose
    def running_time(self):
        return self.state.time

    def get_submodules(self):
        return {
            'display': self.display
        }



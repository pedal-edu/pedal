from pedal.sandbox.mocked import MockModule
from pedal.utilities.system import IS_PYTHON_36


class MockTurtle(MockModule):
    """
    Mock Turtle Module that can be used to trace turtle calls.

    Attributes:
        calls (list of dict): The traced list of calls
        # TODO: it'd be awesome to have a way to construct a representation
        #       of the drawing result that we could autograde!
    """
    module_name = 'turtle'
    FIELDS = ["Canvas", "Pen", "RawPen", "RawTurtle", "Screen",
              "ScrolledCanvas", "Shape", "TK", "TNavigator", "TPen", "Tbuffer",
              "Terminator", "Turtle", "TurtleGraphicsError", "TurtleScreen",
              "TurtleScreenBase", "Vec2D", "addshape", "back", "backward",
              "begin_fill", "begin_poly", "bgcolor", "bgpic", "bk", "bye",
              "circle", "clear", "clearscreen", "clearstamp", "clearstamps",
              "clone", "color", "colormode", "config_dict", "deepcopy",
              "degrees", "delay", "distance", "done", "dot", "down",
              "end_fill", "end_poly", "exitonclick", "fd", "fillcolor",
              "filling", "forward", "get_poly", "get_shapepoly", "getcanvas",
              "getmethparlist", "getpen", "getscreen", "getshapes", "getturtle",
              "goto", "heading", "hideturtle", "home", "ht", "inspect",
              "isdown", "isfile", "isvisible", "join", "left", "listen", "lt",
              "mainloop", "math", "mode", "numinput", "onclick", "ondrag",
              "onkey", "onkeypress", "onkeyrelease", "onrelease",
              "onscreenclick", "ontimer", "pd", "pen", "pencolor", "pendown",
              "pensize", "penup", "pos", "position", "pu", "radians",
              "read_docstrings", "readconfig", "register_shape", "reset",
              "resetscreen", "resizemode", "right", "rt", "screensize",
              "seth", "setheading", "setpos", "setposition", "settiltangle",
              "setundobuffer", "setup", "setworldcoordinates", "setx", "sety",
              "shape", "shapesize", "shapetransform", "shearfactor",
              "showturtle", "simpledialog", "speed", "split", "st", "stamp",
              "sys", "textinput", "tilt", "tiltangle", "time", "title",
              "towards", "tracer", "turtles", "turtlesize", "types", "undo",
              "undobufferentries", "up", "update", "width", "window_height",
              "window_width", "write", "write_docstringdict", "xcor", "ycor"]

    def __init__(self):
        self.calls = []

    def _reset_turtles(self):
        self.calls = []

    def _generate_patches(self):
        if IS_PYTHON_36:
            # Generate patches manually
            return {name: self.getter(name) for name in self.FIELDS}
        else:
            return {'__getattr__': self.getter}

    def getter(self, key):
        " If anything asks, we prevent the module. Except for __file__. "
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

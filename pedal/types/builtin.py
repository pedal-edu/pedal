"""
Type definitions of builtin functions and modules.
"""

from pedal.types.definitions import (UnknownType, FunctionType,
                                     NumType, NoneType, BoolType,
                                     TupleType, ListType, StrType,
                                     FileType, DictType, ModuleType,
                                     SetType, DayType, TimeType,
                                     LiteralNum)

BUILTIN_MODULES = {
    'pprint': ModuleType('pprint',
                         fields={
                             'pprint': FunctionType(name='pprint', returns=NoneType())
                         }),
    'json': ModuleType('json',
                       fields={
                           'loads': FunctionType(name='loads', returns=UnknownType()),
                           'dumps': FunctionType(name='dumps', returns=StrType())
                       }),
    'random': ModuleType('random',
                         fields={
                             'randint': FunctionType(name='randint', returns=NumType())
                         }),
    'string': ModuleType('string',
                         fields={
                             'letters': StrType(empty=False),
                             'digits': StrType(empty=False),
                             'ascii_letters': StrType(empty=False),
                             'punctuation': StrType(empty=False),
                             'printable': StrType(empty=False),
                             'whitespace': StrType(empty=False),
                             'ascii_uppercase': StrType(empty=False),
                             'ascii_lowercase': StrType(empty=False),
                             'hexdigits': StrType(empty=False),
                             'octdigits': StrType(empty=False),
                         }),
    # TODO: Make this an extension in curriculum-ctvt
    'parking': ModuleType('parking',
                          fields={
                              'Time': FunctionType(name='Time', returns=TimeType()),
                              'now': FunctionType(name='now', returns=TimeType()),
                              'Day': FunctionType(name='Day', returns=DayType()),
                              'today': FunctionType(name='today', returns=DayType()),
                          }),
    'math': ModuleType('math',
                       fields={
                           'ceil': FunctionType(name='ceil', returns=NumType()),
                           'copysign': FunctionType(name='copysign', returns=NumType()),
                           'fabs': FunctionType(name='fabs', returns=NumType()),
                           'factorial': FunctionType(name='factorial', returns=NumType()),
                           'floor': FunctionType(name='floor', returns=NumType()),
                           'fmod': FunctionType(name='fmod', returns=NumType()),
                           'frexp': FunctionType(name='frexp', returns=NumType()),
                           'fsum': FunctionType(name='fsum', returns=NumType()),
                           'gcd': FunctionType(name='gcd', returns=NumType()),
                           'isclose': FunctionType(name='isclose', returns=BoolType()),
                           'isfinite': FunctionType(name='isfinite', returns=BoolType()),
                           'isinf': FunctionType(name='isinf', returns=BoolType()),
                           'isnan': FunctionType(name='isnan', returns=BoolType()),
                           'ldexp': FunctionType(name='ldexp', returns=NumType()),
                           'modf': FunctionType(name='modf', returns=NumType()),
                           'trunc': FunctionType(name='trunc', returns=NumType()),
                           'log': FunctionType(name='log', returns=NumType()),
                           'log1p': FunctionType(name='log1p', returns=NumType()),
                           'log2': FunctionType(name='log2', returns=NumType()),
                           'log10': FunctionType(name='log10', returns=NumType()),
                           'pow': FunctionType(name='pow', returns=NumType()),
                           'sqrt': FunctionType(name='sqrt', returns=NumType()),
                           'sin': FunctionType(name='sin', returns=NumType()),
                           'cos': FunctionType(name='cos', returns=NumType()),
                           'tan': FunctionType(name='tan', returns=NumType()),
                           'asin': FunctionType(name='asin', returns=NumType()),
                           'acos': FunctionType(name='acos', returns=NumType()),
                           'atan': FunctionType(name='atan', returns=NumType()),
                           'atan2': FunctionType(name='atan2', returns=NumType()),
                           'hypot': FunctionType(name='hypot', returns=NumType()),
                           'degrees': FunctionType(name='degrees', returns=NumType()),
                           'radians': FunctionType(name='radians', returns=NumType()),
                           'sinh': FunctionType(name='sinh', returns=NumType()),
                           'cosh': FunctionType(name='cosh', returns=NumType()),
                           'tanh': FunctionType(name='tanh', returns=NumType()),
                           'asinh': FunctionType(name='asinh', returns=NumType()),
                           'acosh': FunctionType(name='acosh', returns=NumType()),
                           'atanh': FunctionType(name='atanh', returns=NumType()),
                           'erf': FunctionType(name='erf', returns=NumType()),
                           'erfc': FunctionType(name='erfc', returns=NumType()),
                           'gamma': FunctionType(name='gamma', returns=NumType()),
                           'lgamma': FunctionType(name='lgamma', returns=NumType()),
                           'pi': NumType(),
                           'e': NumType(),
                           'tau': NumType(),
                           'inf': NumType(),
                           'nan': NumType(),
                       })
}


def get_builtin_module(name):
    """
    Given the name of the module, retrieve its TIFA representation.

    Args:
        name:

    Returns:

    """
    return BUILTIN_MODULES.get(name, UnknownType())


def _builtin_sequence_constructor(sequence_type):
    """
    Helper function for creating constructors for the Set and List types.
    These constructors use the subtype of the arguments.

    Args:
        sequence_type (Type): A function for creating new sequence types.
    """

    def sequence_call(tifa, function_type, callee, args, position):
        """

        Args:
            tifa:
            function_type:
            callee:
            args:
            position:

        Returns:

        """
        # TODO: Should inherit the emptiness too
        return_type = sequence_type(empty=True)
        if args:
            return_type.subtype = args[0].index(LiteralNum(0))
            return_type.empty = False
        return return_type

    return sequence_call


def _builtin_zip(tifa, function_type, callee, args, position):
    """
    Definition of the built-in zip function, which consumes a series of
    sequences and returns a list of tuples, with each tuple composed of the
    elements of the sequence paired (or rather, tupled) together.
    """
    if args:
        tupled_types = TupleType(subtypes=[])
        for arg in args:
            tupled_types.subtypes.append(arg.index(0))
        return ListType(tupled_types, empty=False)
    return ListType(empty=True)


# TODO: Exceptions

def get_builtin_function(name):
    """

    Args:
        name:

    Returns:

    """
    # Void Functions
    if name == "print":
        return FunctionType(name="print", returns=NoneType())
    # Math Functions
    elif name in ("int", "abs", "float", "len", "ord", "pow", "round", "sum"):
        return FunctionType(name=name, returns=NumType())
    # Boolean Functions
    elif name in ("bool", "all", "any", "isinstance"):
        return FunctionType(name=name, returns=BoolType())
    # String Functions
    elif name in ("str", 'chr', 'bin', 'repr', 'input'):
        return FunctionType(name=name, returns=StrType())
    # File Functions
    elif name == "open":
        return FunctionType(name="open", returns=FileType())
    # List Functions
    elif name == "map":
        return FunctionType(name="map", returns=ListType(empty=False))
    elif name == "list":
        return FunctionType(name="list",
                            definition=_builtin_sequence_constructor(ListType))
    # Set Functions
    elif name == "set":
        return FunctionType(name="set",
                            definition=_builtin_sequence_constructor(SetType))
    # Dict Functions
    elif name == "dict":
        return FunctionType(name="dict", returns=DictType())
    # Pass through
    elif name == "sorted":
        return FunctionType(name="sorted", returns='identity')
    elif name == "reversed":
        return FunctionType(name="reversed", returns='identity')
    elif name == "filter":
        return FunctionType(name="filter", returns='identity')
    # Special Functions
    elif name == "type":
        return FunctionType(name="type", returns=UnknownType())
    elif name == "range":
        return FunctionType(name="range", returns=ListType(NumType(), empty=False))
    elif name == "dir":
        return FunctionType(name="dir", returns=ListType(StrType(), empty=False))
    elif name == "max":
        return FunctionType(name="max", returns='element')
    elif name == "min":
        return FunctionType(name="min", returns='element')
    elif name == "zip":
        return FunctionType(name="zip", returns=_builtin_zip)
    elif name == "__import__":
        return FunctionType(name="__import__", returns=ModuleType())
    elif name == "globals":
        return FunctionType(name="globals",
                            returns=DictType(keys=StrType(),
                                             values=UnknownType(),
                                             empty=False))
    elif name in ("classmethod", "staticmethod"):
        return FunctionType(name=name, returns='identity')
    elif name in ("__name__",):
        return StrType()


# MatPlotLib Support
_PYPLOT_MODULE = ModuleType('pyplot', fields={
    'plot': FunctionType(name='plot', returns=NoneType()),
    'hist': FunctionType(name='hist', returns=NoneType()),
    'scatter': FunctionType(name='scatter', returns=NoneType()),
    'show': FunctionType(name='show', returns=NoneType()),
    'xlabel': FunctionType(name='xlabel', returns=NoneType()),
    'ylabel': FunctionType(name='ylabel', returns=NoneType()),
    'title': FunctionType(name='title', returns=NoneType()),
})

BUILTIN_MODULES['matplotlib'] = ModuleType('matplotlib',
                                           submodules={
                                               'pyplot': _PYPLOT_MODULE
                                           })


# TODO: Have to figure out how to setup this to be an extension.
#       Problem: It would be imported AFTER Tifa is run...
BUILTIN_MODULES['cisc108'] = ModuleType('cisc108', fields={
    'assert_equal': FunctionType(name='assert_equal', returns=NoneType()),
    'assert_type': FunctionType(name='assert_type', returns=NoneType()),
})

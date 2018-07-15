from pedal.tifa.type_definitions import (UnknownType, RecursedType, FunctionType,
                              ClassType, NumType, NoneType, BoolType,
                              TupleType, ListType, StrType,
                              FileType, DictType, ModuleType, 
                              SetType, GeneratorType, DayType, TimeType)
from pedal.tifa.literal_definitions import LiteralNum

MODULES = {
    'matplotlib': ModuleType('matplotlib',
        submodules={
            'pyplot': ModuleType('pyplot', fields={
                'plot': FunctionType(name='plot', returns=NoneType()),
                'hist': FunctionType(name='hist', returns=NoneType()),
                'scatter': FunctionType(name='scatter', returns=NoneType()),
                'show': FunctionType(name='show', returns=NoneType()),
                'xlabel': FunctionType(name='xlabel', returns=NoneType()),
                'ylabel': FunctionType(name='ylabel', returns=NoneType()),
                'title': FunctionType(name='title', returns=NoneType()),
            })
        }),
    'pprint': ModuleType('pprint',
        fields={
            'pprint': FunctionType(name='pprint', returns=NoneType())
        }),
    'random': ModuleType('random',
        fields={
            'randint': FunctionType(name='randint', returns=NumType())
        }),
    'turtle': ModuleType('turtle',
        fields={
            'forward': FunctionType(name='forward', returns=NoneType()),
            'backward': FunctionType(name='backward', returns=NoneType()),
            'color': FunctionType(name='color', returns=NoneType()),
            'right': FunctionType(name='right', returns=NoneType()),
            'left': FunctionType(name='left', returns=NoneType()),
        }),
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
            'acos': FunctionType(name='acos', returns=NumType()),
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
        }),
}

def _builtin_sequence_constructor(sequence_type):
    '''
    Helper function for creating constructors for the Set and List types.
    These constructors use the subtype of the arguments.
    
    Args:
        sequence_type (Type): A function for creating new sequence types.
    '''
    def sequence_call(tifa, function_type, callee, args, position):
        # TODO: Should inherit the emptiness too
        return_type = sequence_type(empty=True)
        if args:
            return_type.subtype = args[0].index(LiteralNum(0))
        return return_type
    return sequence_call
    
def _builtin_zip(tifa, function_type, callee, args, position):
    '''
    Definition of the built-in zip function, which consumes a series of
    sequences and returns a list of tuples, with each tuple composed of the
    elements of the sequence paired (or rather, tupled) together.
    '''
    if args:
        tupled_types = TupleType(subtypes=[])
        for arg in args:
            tupled_types.append(arg.index(0))
        return ListType(tupled_types)
    return ListType(empty=True)

BUILTINS = {
    # Void Functions
    "print": FunctionType(name="print", returns=NoneType()),
    # Math Functions
    "int": FunctionType(name="int", returns=NumType()),
    "abs": FunctionType(name="abs", returns=NumType()),
    "float": FunctionType(name="float", returns=NumType()),
    "len": FunctionType(name="len", returns=NumType()),
    "ord": FunctionType(name="ord", returns=NumType()),
    "pow": FunctionType(name="pow", returns=NumType()),
    "round": FunctionType(name="round", returns=NumType()),
    "sum": FunctionType(name="sum", returns=NumType()),
    # Boolean Functions
    "bool": FunctionType(name="bool", returns=BoolType()),
    "all": FunctionType(name="all", returns=BoolType()),
    "any": FunctionType(name="any", returns=BoolType()),
    "isinstance": FunctionType(name="isinstance", returns=BoolType()),
    # String Functions
    "input": FunctionType(name="input", returns=StrType()),
    "str": FunctionType(name="str", returns=StrType()),
    "chr": FunctionType(name="chr", returns=StrType()),
    "repr": FunctionType(name="repr", returns=StrType()),
    # File Functions
    "open": FunctionType(name="open", returns=FileType()),
    # List Functions
    "map": FunctionType(name="map", returns=ListType()),
    "list": FunctionType(name="list", 
                         definition=_builtin_sequence_constructor(ListType)),
    # Set Functions
    "set": FunctionType(name="set", 
                         definition=_builtin_sequence_constructor(SetType)),
    # Dict Functions
    "dict": FunctionType(name="dict", returns=DictType()),
    # Pass through
    "sorted": FunctionType(name="sorted", returns='identity'),
    "reversed": FunctionType(name="reversed", returns='identity'),
    "filter": FunctionType(name="filter", returns='identity'),
    # Special Functions
    "range": FunctionType(name="range", returns=ListType(NumType())),
    "dir": FunctionType(name="dir", returns=ListType(StrType())),
    "max": FunctionType(name="max", returns='element'),
    "min": FunctionType(name="min", returns='element'),
    "zip": FunctionType(name="zip", returns=_builtin_zip)
}
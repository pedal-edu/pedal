"""
A collection of types.

TODO: Make the types all respect the type heirarchy properly.
For example, SetType should not descend from ListType, that's just lazy.
Instead, create a hierachy based on form and not just function.
"""

import ast

from pedal.utilities.dictionaries import extend_dictionary


def are_literals_equal(first, second):
    """
    Determines if two literals have the exact same value.
    Checks nested structures.

    Args:
        first (Any):
        second (Any):

    Returns:
        bool: Whether or not they are equal.
    """
    if first is None or second is None:
        return False
    elif not isinstance(first, type(second)):
        return False
    else:
        if isinstance(first, LiteralTuple):
            if len(first.value) != len(second.value):
                return False
            for l, s in zip(first.value, second.value):
                if not are_literals_equal(l, s):
                    return False
            return True
        elif not isinstance(first, LiteralValue):
            return True
        else:
            return first.value == second.value


class LiteralValue:
    """
    A special literal representation of a value, used to represent access on
    certain container types.
    """

    def __init__(self, value):
        self.value = value


class LiteralNum(LiteralValue):
    """
    Used to capture indexes of containers.
    """

    def type(self):
        """

        Returns:

        """
        return NumType()


class LiteralBool(LiteralValue):
    def type(self):
        """

        Returns:

        """
        return BoolType()


class LiteralStr(LiteralValue):
    def type(self):
        """

        Returns:

        """
        return StrType()


class LiteralTuple(LiteralValue):
    def type(self):
        """

        Returns:

        """
        return TupleType(self.value)


class LiteralNone(LiteralValue):
    def type(self):
        """

        Returns:

        """
        return NoneType()


class Type:
    """
    Parent class for all other types, used to provide a common interface.

    TODO: Handle more complicated object-oriented types and custom types
        (classes).
    """
    fields = {}
    immutable = False
    singular_name = 'a type'

    def clone(self):
        """

        Returns:

        """
        return self.__class__()

    def __str__(self):
        return str(self.__class__.__name__)

    def precise_description(self):
        """

        Returns:

        """
        return self.singular_name

    def clone_mutably(self):
        """

        Returns:

        """
        if self.immutable:
            return self.clone()
        else:
            return self

    def index(self, i):
        """

        Args:
            i:

        Returns:

        """
        return self.clone()

    def iterate(self, i):
        """

        Args:
            i:

        Returns:

        """
        return self.index(i)

    def load_attr(self, attr):
        """

        Args:
            attr:
            tifa:
            callee:
            callee_position:

        Returns:

        """
        if attr in self.fields:
            return self.fields[attr]
        return UnknownType()

    def is_empty(self):
        """

        Returns:

        """
        return True

    def is_equal(self, other):
        """

        Args:
            other:

        Returns:

        """
        # TODO: Make this more sophisticated!
        if type(self) not in TYPE_LOOKUPS:
            return False
        return other in TYPE_LOOKUPS[type(self)]

    def is_instance(self, other):
        """

        Args:
            other:

        Returns:

        """
        # TODO: Implement this correctly
        return self.is_equal(other)


class UnknownType(Type):
    """
    A special type used to indicate an unknowable type.
    """
    singular_name = "an unknown type"


class RecursedType(Type):
    """
    A special type used as a placeholder for the result of a
    recursive call that we have already process. This type will
    be dominated by any actual types, but will not cause an issue.
    """


class FunctionType(Type):
    """
    
    Special values for `returns`:
        identity: Returns the first argument's type
        element: Returns the first argument's first element's type
        void: Returns the NoneType
    """
    singular_name = 'a function'

    def __init__(self, definition=None, name="*Anonymous", returns=None):
        if returns is not None and definition is None:
            if returns == 'identity':
                # TODO: Determine if these can be extracted to be constant?
                def definition(ti, ty, na, args, ca):
                    """ Identify function definition """
                    if args:
                        return args[0].clone()
                    return UnknownType()
            elif returns == 'element':
                def definition(ti, ty, na, args, ca):
                    """ Element function definition """
                    if args:
                        return args[0].index(0)
                    return UnknownType()
            elif returns == 'void':
                def definition(ti, ty, na, args, ca):
                    """ Void function definition """
                    return NoneType()
            else:
                def definition(ti, ty, na, args, ca):
                    """ Generic function """
                    return returns.clone()
        self.definition = definition
        self.name = name
        self.returns = returns

    def clone(self):
        """ Create a deep copy of this function type. """
        returns = self.returns if self.returns is None else self.returns.clone()
        return FunctionType(definition=self.definition,
                            name=self.name, returns=returns)


class ClassType(Type):
    """

    """
    singular_name = 'a class'

    def __init__(self, name):
        self.name = name
        self.fields = {}
        self.scope_id = None

    def add_attr(self, name, type):
        """

        Args:
            name:
            type:
        """
        self.fields[name] = type

    def get_constructor(self):
        """

        Returns:

        """
        i = InstanceType(self)
        return FunctionType(name='__init__', returns=i)

    def clone(self):
        """

        Returns:

        """
        return ClassType(self.name)


class InstanceType(Type):
    """

    """

    def __init__(self, parent):
        self.parent = parent
        self.fields = parent.fields

    def __str__(self):
        return "InstanceTypeOf" + str(self.parent.name)

    def clone(self):
        """

        Returns:

        """
        return InstanceType(self.parent)

    def add_attr(self, name, type):
        """

        Args:
            name:
            type:
        """
        # TODO: What if this is a type change?
        self.parent.add_attr(name, type)


class NumType(Type):
    """ Basic Numeric Type (integers and floats) """
    singular_name = 'a number'
    immutable = True

    def index(self, i):
        """ Cannot index a numeric """
        return UnknownType()


class NoneType(Type):
    singular_name = 'a None'
    immutable = True


class BoolType(Type):
    singular_name = 'a boolean'
    immutable = True


class CustomType(Type):
    def __init__(self, name):
        self.singular_name = name


class IndexableType(Type):
    """
    An abstract base class to represent a type that can be accessed via
    an integer index.
    """

    def __init__(self, subtypes=None):
        """
        Create a new instance of this type.

        Args:
            subtypes (Iterable[Type]): An iterable of types.
        """
        if subtypes is None:
            subtypes = []
        self.subtypes = subtypes
        self.empty = bool(subtypes)

    def index(self, i):
        """
        Retrieves the type at the given index of this indexable type.

        Args:
            i: Either a LiteralNum or an actual integer.

        Returns:
            Type: Whatever type was at that index.
        """
        if isinstance(i, LiteralNum):
            return self.subtypes[i.value].clone()
        else:
            return self.subtypes[i].clone()

    def clone(self):
        """
        Makes a duplicate of this type by creating a new instance of
        the type and passing in a list of cloned values.

        Returns:
            IndexableType: A copy of this type.
        """
        return type(self)(subtypes=[t.clone() for t in self.subtypes])


class TupleType(IndexableType):
    """ Type representing a tuple """
    singular_name = 'a tuple'
    immutable = True


class ListType(Type):
    """ A ListType """
    singular_name = 'a list'

    def __init__(self, subtype=None, empty=True):
        if subtype is None:
            subtype = UnknownType()
        self.subtype = subtype
        self.empty = empty

    def precise_description(self):
        """ String with all the type information. """
        if self.empty:
            descr = "an empty list"
        else:
            descr = "a list"
        if not isinstance(self.subtype, UnknownType):
            descr += " of "+self.subtype.precise_description()
        return descr

    def index(self, i):
        """

        Args:
            i:

        Returns:

        """
        if isinstance(i, LiteralNum):
            return self.subtype.clone()
        else:
            return UnknownType()

    def clone(self):
        """

        Returns:

        """
        return ListType(self.subtype.clone(), self.empty)

    def load_attr(self, attr):
        """

        Args:
            attr:
            tifa:
            callee:
            callee_position:

        Returns:

        """
        if attr == 'append':
            def _append(tifa, function_type, callee, args, position):
                if args:
                    cloned_type = ListType(subtype=args[0].clone(),
                                           empty=False)
                    if callee:
                        tifa.append_variable(callee, cloned_type, position)
                    self.empty = False
                    self.subtype = args[0]
                return NoneType()

            return FunctionType(_append, 'append')
        # Extend, Pop
        return Type.load_attr(self, attr)

    def is_empty(self):
        """

        Returns:

        """
        return self.empty


class StrType(Type):
    """

    """
    singular_name = 'a string'

    def __init__(self, empty=False):
        self.empty = empty

    def index(self, i):
        """

        Args:
            i:

        Returns:

        """
        if isinstance(i, LiteralNum):
            return StrType()
        else:
            return UnknownType()


    def is_empty(self):
        """

        Returns:

        """
        return self.empty

    fields = extend_dictionary(Type.fields, {})
    immutable = True


StrType.fields.update({
    # Methods that return strings
    "capitalize": FunctionType(name='capitalize', returns=StrType()),
    "center": FunctionType(name='center', returns=StrType()),
    "expandtabs": FunctionType(name='expandtabs', returns=StrType()),
    "join": FunctionType(name='join', returns=StrType()),
    "ljust": FunctionType(name='ljust', returns=StrType()),
    "lower": FunctionType(name='lower', returns=StrType()),
    "lstrip": FunctionType(name='lstrip', returns=StrType()),
    "replace": FunctionType(name='replace', returns=StrType()),
    "rjust": FunctionType(name='rjust', returns=StrType()),
    "rstrip": FunctionType(name='rstrip', returns=StrType()),
    "strip": FunctionType(name='strip', returns=StrType()),
    "swapcase": FunctionType(name='swapcase', returns=StrType()),
    "title": FunctionType(name='title', returns=StrType()),
    "translate": FunctionType(name='translate', returns=StrType()),
    "upper": FunctionType(name='upper', returns=StrType()),
    "zfill": FunctionType(name='zfill', returns=StrType()),
    # Methods that return numbers
    "count": FunctionType(name='count', returns=NumType()),
    "find": FunctionType(name='find', returns=NumType()),
    "rfind": FunctionType(name='rfind', returns=NumType()),
    "index": FunctionType(name='index', returns=NumType()),
    "rindex": FunctionType(name='rindex', returns=NumType()),
    # Methods that return booleans
    "startswith": FunctionType(name='startswith', returns=BoolType()),
    "endswith": FunctionType(name='endswith', returns=BoolType()),
    "isalnum": FunctionType(name='isalnum', returns=BoolType()),
    "isalpha": FunctionType(name='isalpha', returns=BoolType()),
    "isdigit": FunctionType(name='isdigit', returns=BoolType()),
    "islower": FunctionType(name='islower', returns=BoolType()),
    "isspace": FunctionType(name='isspace', returns=BoolType()),
    "istitle": FunctionType(name='istitle', returns=BoolType()),
    "isupper": FunctionType(name='isupper', returns=BoolType()),
    # Methods that return List of Strings
    "rsplit": FunctionType(name='rsplit', returns=ListType(StrType(), empty=False)),
    "split": FunctionType(name='split', returns=ListType(StrType(), empty=False)),
    "splitlines": FunctionType(name='splitlines', returns=ListType(StrType(), empty=False))
})


class FileType(Type):
    singular_name = 'a file'

    def index(self, i):
        """

        Args:
            i:

        Returns:

        """
        return StrType()

    fields = extend_dictionary(Type.fields, {
        'close': FunctionType(name='close', returns='void'),
        'read': FunctionType(name='read', returns=StrType()),
        'readlines': FunctionType(name='readlines', returns=ListType(StrType(), False))
    })

    def is_empty(self):
        """

        Returns:

        """
        return False


class DictType(Type):
    """

    """
    singular_name = 'a dictionary'

    def precise_description(self):
        """

        Returns:

        """
        base = "a dictionary"
        if self.literals:
            base += " mapping "
            # TODO: Handle recursive precise names more correctly
            base += ", ".join("{!r} to {}".format(l.value, r.precise_description())
                              for l, r in zip(self.literals, self.values))
        elif self.keys:
            keys = self.keys[0] if isinstance(self.keys, list) else self.keys
            values = self.values[0] if isinstance(self.values, list) else self.values
            base += " mapping {}".format(keys.precise_description())
            base += " to {}".format(values.precise_description())
        return base

    def __init__(self, empty=False, literals=None, keys=None, values=None):
        self.empty = empty
        self.literals = literals
        self.values = values
        self.keys = keys

    def clone(self):
        """

        Returns:

        """
        # TODO: Pretty sure these should be recursively cloning fields
        return DictType(self.empty, self.literals, self.keys, self.values)

    def is_empty(self):
        """

        Returns:

        """
        return self.empty

    def has_literal(self, l):
        """

        Args:
            l:

        Returns:

        """
        for literal, value in zip(self.literals, self.values):
            if are_literals_equal(literal, l):
                return value
        return None

    def _access_item(self, i, get_keys=False):
        if self.empty:
            return UnknownType()
        elif self.literals is not None:
            for literal, value in zip(self.literals, self.values):
                if are_literals_equal(literal, i):
                    return value.clone()
            return UnknownType()
        elif get_keys:
            # TODO: Handle multiple keys/values
            return self.keys[0].clone()
        else:
            return self.values[0].clone()

    def index(self, i):
        """

        Args:
            i:

        Returns:

        """
        return self._access_item(i, False)

    def iterate(self, i):
        """

        Args:
            i:

        Returns:

        """
        return self._access_item(i, True)

    def update_key(self, literal_key, type):
        """

        Args:
            literal_key:
            type:
        """
        self.literals.append(literal_key)
        self.values.append(type)

    def load_attr(self, attr):
        """

        Args:
            attr:
            tifa:
            callee:
            callee_position:

        Returns:

        """
        if attr == 'items':
            def _items(tifa, function_type, callee, args, position):
                if self.literals is None:
                    return ListType(TupleType([self.keys, self.values]),
                                    empty=False)
                else:
                    return ListType(TupleType([self.literals[0].type(),
                                               self.values[0]]),
                                    empty=False)

            return FunctionType(_items, 'items')
        elif attr == 'keys':
            def _keys(tifa, function_type, callee, args, position):
                if self.literals is None:
                    return ListType(self.keys, empty=False)
                else:
                    return ListType(self.literals[0].type(), empty=False)

            return FunctionType(_keys, 'keys')
        elif attr == 'values':
            def _values(tifa, function_type, callee, args, position):
                if self.literals is None:
                    return ListType(self.values, empty=False)
                else:
                    return ListType(self.values[0], empty=False)

            return FunctionType(_values, 'values')
        return Type.load_attr(self, attr)


class ModuleType(Type):
    """

    """
    singular_name = 'a module'

    def __init__(self, name="*UnknownModule", submodules=None, fields=None):
        self.name = name
        if submodules is None:
            submodules = {}
        self.submodules = submodules
        if fields is None:
            fields = {}
        self.fields = fields

    def clone(self):
        """ Create a copy of this ModuleType """
        submodules = {n: v.clone() for n, v in self.submodules.items()}
        fields = {n: v.clone() for n, v in self.fields.items()}
        return ModuleType(name=self.name, submodules=submodules, fields=fields)


class SetType(ListType):
    singular_name = 'a set'


class FrozenSetType(SetType):
    """ Type representing a frozenset """
    singular_name = 'a frozen set'
    immutable = True


class GeneratorType(ListType):
    singular_name = 'a generator'


# TODO: Move these into curriculum-ctvt

class TimeType(Type):
    singular_name = 'a time of day'


class DayType(Type):
    singular_name = 'a day of the week'


try:
    from numbers import Number
except Exception:
    Number = int

TYPE_LOOKUPS = {
    FunctionType: ('function', FunctionType, 'FunctionType'),
    ClassType: ('class', ClassType, 'ClassType'),
    InstanceType: ('instance', InstanceType, 'InstanceType'),
    NumType: ('num', int, float, complex, NumType, Number, 'NumType'),
    BoolType: ('bool', bool, BoolType, 'BoolType'),
    NoneType: ('None', None, NoneType, 'NoneType'),
    TupleType: ('tuple', tuple, TupleType, 'TupleType'),
    ListType: ('list', list, ListType, 'ListType'),
    StrType: ('str', str, StrType, 'StrType'),
    FileType: ('file', FileType, 'FileType'),
    DictType: ('dict', dict, DictType, 'DictType'),
    SetType: ('set', set, SetType, 'SetType'),
}


TYPE_STRINGS = {
    "str": StrType, "string": StrType,
    "num": NumType, "number": NumType,
    "int": NumType, "integer": NumType, "float": NumType,
    "complex": NumType,
    "bool": BoolType, "boolean": BoolType,
    "none": NoneType, "nonetype": NoneType,
    "dict": DictType, "dictionary": DictType,
    "list": ListType,
    "tuple": TupleType,
    "set": SetType,
    "file": FileType,
    "func": FunctionType, "function": FunctionType,
    "class": ClassType,
}


class TypeSpace:
    def has(self, name):
        return False

    def get(self, name):
        return None

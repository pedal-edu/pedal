"""
Fresh approach to having types in Pedal.

We will use inheritance to share behavior, not to check identity.
Instead we'll have our own set of fields to handle things like that.

Polymorphism, subtyping, there's a lot to unpack here.

Where possible, let's try to interface with `typing`, shall we?


Still to do:
 - [X] specify_type
 - [ ] convert_type
 - [ ] TypeUnion
 - [X] DictType
 - [X] FileType
 - [X] ModuleType
 - [X] GeneratorType
 - [X] SetType, FrozenSetType
 - [ ] LiteralTuple
 - [ ] Binary operations
 - [ ] Unary operations
 - [X] Orderable operations
 - [X] Indexing operations
 - [X] Iteration operations
 - [X] Membership operations

 - [ ] RecursedType

 - [*] Finish function definitions
 - [ ] Finish container literals (do condensing)
 - [ ] Finish Subscripting
 - [X] Unary Ops
 - [X] Finish collection loops
 - [X] Finish While
 - [X] Finish With
 - [ ] Finish evaluate_type
 - [ ] Finish built-in constructor types

"""
from typing import Set
from pedal.utilities.text import join_list_with_and, add_indefinite_article


BUILTIN_MODULES = {}
BUILTIN_NAMES = {}

_MODULE_LOADERS = {}


def register_builtin_module(name, module_function):
    _MODULE_LOADERS[name] = module_function


# TODO: Should tie type system into Report
def reset_builtin_modules():
    BUILTIN_MODULES.clear()
    for name, module_function in _MODULE_LOADERS.items():
        BUILTIN_MODULES[name] = module_function()


def void_definition(tifa, function, callee, arguments, named_arguments, location):
    return NoneType()


def identity_definition(tifa, function, callee, arguments, named_arguments, location):
    if function and function.the_self:
        # If method, return self
        return function.the_self
    elif arguments:
        # Get the first argument
        return arguments[0]
    elif named_arguments:
        # Get the first named argument as the key
        first_key, first_value = next(iter(named_arguments))
        # If **kwargs, then retrieve first arbitrary key
        if first_key is None:
            _, first_kwarg_value = next(iter(first_value))
            return first_kwarg_value
        return first_value
    return ImpossibleType()


def element_definition(tifa, function, callee, arguments, named_arguments, location):
    """ Element function definition """
    return arguments[0].index(IntType()) if arguments else ImpossibleType()


class Type:
    # Class static
    name: str
    singular_name: str
    plural_name: str
    immutable: bool
    # Per-Class and per-instance
    fields: dict
    parents: list
    # Default Universal Fields
    is_empty = False
    orderable = frozenset()

    def __init__(self):
        self.fields = self.fields.copy()

    def clone(self):
        """ Make a new instance of this Type based on the old instance """
        return self.__class__()

    def shallow_clone(self):
        return self.clone()

    def __str__(self):
        return str(self.__class__.__name__)

    def precise_description(self):
        """
        Returns: A human-friendly but very precise description of this type
        """
        return self.singular_name

    def clone_mutably(self):
        """ Makes a new instance IF the type is immutable; otherwise returns this instance. """
        if self.immutable:
            return self.clone()
        else:
            return self

    def set_index(self, index, value):
        return ImpossibleType()

    def index(self, key):
        """ Access a specific element given the key """
        return ImpossibleType()

    def allows_membership(self, key):
        return False

    def iterate(self):
        """ Returns a single type representing the iteration variable """
        return ImpossibleType()

    def break_apart(self):
        """ Returns a generator of the types as requested """
        while True:
            yield ImpossibleType()

    def get_attr(self, field: str):
        value = self.find_field(field, set())
        if value is None:
            return ImpossibleType()
        return value

    def has_attr(self, field: str):
        return self.find_field(field, set()) is not None

    def add_attr(self, field: str, value):
        self.fields[field] = value

    def find_field(self, field: str, seen: set):
        if field in self.fields:
            return self.fields[field]
        seen.add(self)
        for parent in self.parents:
            if parent not in seen:
                result = parent.find_field(field, seen)
                if result:
                    return result
        return

    def list_fields(self, seen=None):
        if seen is None:
            seen = set()
        for field in self.fields:
            yield field
        seen.add(self)
        for parent in self.parents:
            if parent not in seen:
                yield from parent.list_fields(seen)

    def is_subtype(self, other, seen, indent=0):
        if isinstance(self, AnyType) or isinstance(other, AnyType):
            return True
        if type(self) == type(other):
            return True
        if self in seen:
            return True
        seen.add(self)
        return any(parent.is_subtype(other, seen, 1+indent) for parent in self.parents)

    def specify_subtype(self, receiving_type):
        if isinstance(receiving_type, AnyType):
            return self
        return receiving_type

    def add_type_arguments(self, type_arguments):
        """
        Add the given type arguments to this type, in whatever way makes sense
        for the child class.

        Args:
            type_arguments (tuple[Type]): The type arguments to add.
                This will always be a tuple, even if there is only one argument.
        """
        return self

    @staticmethod
    def definition(tifa, function, callee, arguments, named_arguments, location):
        return ImpossibleType()

    def as_type(self, tifa=None, location=None):
        return self

    def is_equal(self, other):
        """ DEPRECATED """
        import pedal.types.normalize as normalize
        if other == 'num':
            other = normalize.NumType
        return is_subtype(self, normalize.normalize_type(other).as_type())


class AnyType(Type):
    """
    A special type used to indicate an unknown type.

    This is our Top Type!
    """
    name = "Unknown"
    singular_name = "an unknown value"
    plural_name = "unknown values"
    immutable = False
    fields = {}
    parents = []

    def set_index(self, index, value):
        return AnyType()

    def index(self, key):
        """ Access a specific element given the key """
        return AnyType()

    def allows_membership(self, key):
        return True

    def iterate(self):
        """ Returns a single type representing the iteration variable """
        return AnyType()

    def break_apart(self):
        """ Returns a generator of the types as requested """
        while True:
            yield AnyType()

    def get_attr(self, field: str):
        return AnyType()


class ImpossibleType(Type):
    """
    A special type used to indicate a type situation that is impossible.
    The real type would be unknowable because of invalid code.

    This is our Bottom Type!
    """
    name = "Impossible"
    singular_name = "an impossible value"
    plural_name = "impossible value"
    immutable = False
    fields = {}
    parents = []


class NoneType(Type):
    name = "NoneType"
    singular_name = "a None"
    plural_name = "None"
    immutable = True
    fields = {}
    parents = []


class TypeUnion(Type):
    """
    TODO: Decide if using!
    A type that could be one of several possible types
    """
    name = "Type Union"
    singular_name = "one of several possible types"
    plural_name = "several possible types"
    immutable = False
    fields = {}
    parents = []

    def __init__(self, possible_types):
        super().__init__()
        self.possible_types = set(possible_types)


class FunctionType(Type):
    name = 'Function'
    singular_name = 'a function'
    plural_name = 'functions'
    immutable = True
    fields = {}
    parents = []
    #: the_self: Type | None

    def __init__(self, name="*Anonymous", definition=None, returns=None, the_self=None):
        super().__init__()
        if definition is None:
            if returns is None or returns == 'void':
                definition = void_definition
            elif returns == 'identity':
                definition = identity_definition
            elif returns == 'element':
                definition = element_definition
            else:
                def definition(tifa, function, callee, arguments, named_arguments, location):
                    """ Generic function """
                    return returns().clone()
        self.definition = definition
        self.name = name
        self.returns = returns
        self.the_self = the_self

    def clone(self):
        """ Create a deep copy of this function type. """
        returns = self.returns
        the_self = self.the_self if self.the_self is None else self.the_self.clone()
        return FunctionType(name=self.name, definition=self.definition, returns=returns, the_self=the_self)

    def clone_mutably(self):
        returns = self.returns
        the_self = self.the_self if self.the_self is None else self.the_self.clone_mutably()
        return FunctionType(name=self.name, definition=self.definition, returns=returns, the_self=the_self)

    def as_method(self, the_self):
        return FunctionType(name=self.name, definition=self.definition, returns=self.returns, the_self=the_self)


class NumType(Type):
    name = "Num"
    singular_name = "a number"
    plural_name = "numbers"
    immutable = True
    fields = {}
    parents = []


class IntType(Type):
    name = "Integer"
    singular_name = "an integer"
    plural_name = "integers"
    immutable = True
    fields = {}
    parents = [NumType()]

    def is_subtype(self, other, seen, indent=0):
        if isinstance(other, LiteralInt):
            return True
        return super().is_subtype(other, seen, indent)


class FloatType(Type):
    name = "Float"
    singular_name = "a float"
    plural_name = "floats"
    immutable = True
    fields = {}
    parents = [NumType()]

    def is_subtype(self, other, seen, indent=0):
        if isinstance(other, LiteralFloat):
            return True
        return super().is_subtype(other, seen, indent)


class BoolType(Type):
    name = "Boolean"
    singular_name = "a boolean"
    plural_name = "booleans"
    immutable = True
    fields = {}
    parents = []

    def is_subtype(self, other, seen, indent=0):
        if isinstance(other, LiteralBool):
            return True
        return super().is_subtype(other, seen, indent)


class ExceptionType(Type):
    name = "Exception"
    singular_name = "an exception"
    plural_name = "exceptions"
    immutable = False
    fields = {}
    parents = []


class StrType(Type):
    name = "String"
    singular_name = "a string"
    plural_name = "strings"
    immutable = True
    # Local
    is_empty: bool
    fields = {}
    parents = []

    def __init__(self, is_empty=False):
        super().__init__()
        self.is_empty = is_empty

    def index(self, key):
        # TODO: Support a flag for whether Numbers are allowed for Integers
        return StrType(False) if is_subtype(key, IntType()) else ImpossibleType()

    def is_subtype(self, other, seen, indent=0):
        if isinstance(other, LiteralStr):
            return True
        return super().is_subtype(other, seen, indent)

    def iterate(self):
        return StrType(False)

    def break_apart(self):
        while True:
            yield StrType(False)

    def allows_membership(self, key):
        return is_subtype(key, StrType())


class ElementContainerType(Type):
    is_empty: bool
    element_type: Type
    _singular_names: tuple
    _plural_names: tuple

    def __init__(self, is_empty=True, element_type=None):
        super().__init__()
        self.is_empty = is_empty
        if element_type is None:
            element_type = AnyType()
        self.element_type = element_type

    def __str__(self):
        # TODO: Handle other recursively defined definitions and nested recursion
        if self == self.element_type:
            return f"Recursively-defined {'Empty' if self.is_empty else ''}{self.name}Type"
        return f"{'Empty' if self.is_empty else ''}{self.name}Type[{self.element_type}]"

    @property
    def singular_name(self):
        descr = self._singular_names[self.is_empty]
        if not isinstance(self.element_type, AnyType):
            descr += " of " + self.element_type.plural_name
        return descr

    @property
    def plural_name(self):
        descr = self._plural_names[self.is_empty]
        if not isinstance(self.element_type, AnyType):
            descr += " of " + self.element_type.plural_name
        return descr

    def clone(self):
        return self.__class__(self.is_empty, self.element_type.clone())

    def shallow_clone(self):
        return self.__class__(self.is_empty, self.element_type)

    def is_subtype(self, other, seen, indent=0):
        if isinstance(self, AnyType) or isinstance(other, AnyType):
            return True
        if self in seen:
            return True
        seen.add(self)
        if type(self) == type(other) or any(parent.is_subtype(other, seen, indent+1) for parent in self.parents):
            other_element_type = other.element_type
            result = self.element_type.is_subtype(other_element_type, seen, indent+1)
            return result
        return False

    def specify_subtype(self, receiving_type):
        if isinstance(receiving_type, AnyType):
            return self
        if type(self) == type(receiving_type):
            receiving_type.element_type = self.element_type.specify_subtype(receiving_type.element_type)
            return receiving_type

    def add_type_arguments(self, type_arguments):
        if isinstance(type_arguments, tuple):
            self.element_type = (type_arguments[0] if len(type_arguments) == 1
                                 else TupleType(type_arguments))
        else:
            self.element_type = type_arguments
        return self

    def break_apart(self):
        while True:
            yield self.element_type

    def iterate(self):
        return self.element_type

    def allows_membership(self, key):
        return is_subtype(key, self.element_type)

    def as_type(self, tifa=None, location=None):
        return self.__class__(self.is_empty, self.element_type.as_type(tifa, location))


class SetType(ElementContainerType):
    name = "Set"
    immutable = False
    fields = {}
    parents = []
    _singular_names = ("a set", "an empty set")
    _plural_names = ("sets", "empty sets")

    @staticmethod
    def add(tifa, function, callee, arguments, named_arguments, location):
        if len(arguments) == 1:
            if not function or not function.the_self:
                raise ValueError("Attempted to call add method statically")
            self_type = function.the_self
            self_type.element_type = arguments[0]
            self_type.is_empty = False
            if callee:
                tifa.append_variable(callee.name, callee.type, location)
        return NoneType()


class FrozenSetType(ElementContainerType):
    name = "FrozenSet"
    immutable = True
    fields = {}
    parents = []
    _singular_names = ("a frozen set", "an empty, frozen set")
    _plural_names = ("frozen sets", "empty frozen sets")


class ListType(ElementContainerType):
    name = "List"
    immutable = False
    # Local
    fields = {}
    parents = []
    _singular_names = ("a list", "an empty list")
    _plural_names = ("lists", "empty lists")
    # TODO: Add in support for "protected_fields"
    protected_fields = ["append"]

    def index(self, key):
        # TODO: Support a flag for whether Numbers are allowed for Integers
        return self.element_type if is_subtype(key, IntType()) else ImpossibleType()

    @staticmethod
    def append(tifa, function, callee, arguments, named_arguments, location):
        if len(arguments) == 1:
            if not function or not function.the_self:
                raise ValueError("Attempted to call append method statically")
            self_type = function.the_self
            if not is_subtype(self_type.element_type, arguments[0]):
                tifa._issue('type_change_append', location,
                            self_type.element_type, arguments[0])
            self_type.element_type = arguments[0]
            self_type.is_empty = False
            if callee:
                tifa.append_variable(callee.name, callee.type, location)
        return NoneType()

    # TODO: extend function!


class GeneratorType(ElementContainerType):
    name = "Generator"
    immutable = True
    # Local
    fields = {}
    parents = []
    _singular_names = ("a generator", "an empty generator")
    _plural_names = ("generators", "empty generators")

    def index(self, key):
        return ImpossibleType()


class TupleType(Type):
    name = "Tuple"
    immutable = True
    # Local
    is_empty: bool
    element_types: tuple #: tuple[Type]
    fields = {}
    parents = []

    def __init__(self, element_types=None):
        super().__init__()
        if element_types is None:
            element_types = tuple()
        self.element_types = element_types
        self.is_empty = not element_types

    @property
    def singular_name(self):
        if self.is_empty:
            descr = "an empty tuple"
        else:
            descr = "a tuple"
        if not isinstance(self.element_types, AnyType):
            descr += " of " + join_list_with_and(t.singular_name for t in self.element_types)
        return descr

    @property
    def plural_name(self):
        if self.is_empty:
            descr = "empty tuples"
        else:
            descr = "tuples"
        if not isinstance(self.element_types, AnyType):
            descr += " of " + join_list_with_and(t.singular_name for t in self.element_types)
        return descr

    def clone(self):
        return TupleType(tuple(t.clone() for t in self.element_types))

    def shallow_clone(self):
        return TupleType(tuple(self.element_types))

    def index(self, key):
        # TODO: Support a flag for whether Numbers are allowed for Integers
        # TODO: Return a TypeUnion instead of the first one
        if isinstance(key, LiteralInt):
            if key.value >= len(self.element_types):
                return ImpossibleType()
            return self.element_types[key.value]
        elif isinstance(key, int):
            if key >= len(self.element_types):
                return ImpossibleType()
            return self.element_types[key]
        elif is_subtype(key, IntType()) and self.element_types:
            return self.element_types[0]
        else:
            return ImpossibleType()

    def iterate(self):
        if len(self.element_types) == 0:
            return AnyType()
        potential = widest_type(self.element_types)
        if potential is not None:
            return potential
        return TypeUnion(self.element_types)

    def break_apart(self):
        for t in self.element_types:
            yield t
        while True:
            yield ImpossibleType()

    def allows_membership(self, key):
        return any(is_subtype(key, t) for t in self.element_types)

    def is_subtype(self, other, seen, indent=0):
        if isinstance(self, AnyType) or isinstance(other, AnyType):
            return True
        if self in seen:
            return True
        seen.add(self)
        if type(self) == type(other) or any(parent.is_subtype(other, seen, indent + 1) for parent in self.parents):
            return all(e.is_subtype(e2, seen, indent+1)
                       for e, e2 in zip(self.element_types, other.element_types))
        return False

    def specify_subtype(self, receiving_type):
        if isinstance(receiving_type, AnyType):
            return self
        if type(self) == type(receiving_type) and len(self.element_types) == len(receiving_type.element_types):
            receiving_type.element_types = tuple((e.specify_subtype(e2)
                                                  for e, e2 in zip(self.element_types,
                                                                   receiving_type.element_types)))
            return receiving_type

    def add_type_arguments(self, type_arguments):
        self.element_types = type_arguments
        return self

    def as_type(self, tifa=None, location=None):
        return TupleType([t.as_type(tifa, location) for t in self.element_types])


class DictType(Type):
    name = "Dictionary"
    immutable = False
    # Local
    fields = {}
    parents = []
    _singular_names = ("a dictionary", "an empty dictionary")
    _plural_names = ("dictionaries", "empty dictionaries")
    element_types: list

    def __init__(self, element_types=None):
        super().__init__()
        if element_types is None:
            element_types = []
        self.element_types = element_types

    def _find_best_item(self, key):
        if isinstance(key, LiteralValue):
            for index, (potential_key, value) in enumerate(self.element_types):
                if isinstance(potential_key, LiteralValue):
                    if potential_key.value == key.value:
                        return index, potential_key, value
        candidates = [(index, potential_key, value)
                      for index, (potential_key, value) in enumerate(self.element_types)
                      if is_subtype(key, potential_key)]
        # TODO: Have some sense of "best" and "worst" subtype relationships?
        return candidates[0] if candidates else (None, None, None)


    @property
    def is_empty(self):
        return not self.element_types

    @property
    def singular_name(self):
        base = self._singular_names[self.is_empty]
        if len(self.element_types) == 1:
            key, value = next(iter(self.element_types))
            base += f" mapping {key.plural_name} to {value.plural_name}"
        elif len(self.element_types) > 1:
            base += " mapping " + join_list_with_and(f"{key.singular_name} to {value.plural_name}"
                                                     for key, value in self.element_types)
        return base

    @property
    def plural_name(self):
        base = self._plural_names[self.is_empty]
        if len(self.element_types) == 1:
            key, value = next(iter(self.element_types))
            base += f" mapping {key.plural_name} to {value.plural_name}"
        elif len(self.element_types) > 1:
            base += " mapping " + join_list_with_and(f"{key.singular_name} to {value.plural_name}"
                                                     for key, value in self.element_types)
        return base

    def clone(self):
        return DictType([(key.clone(), value.clone()) for key, value in self.element_types])

    def shallow_clone(self):
        return DictType(list(self.element_types))

    def is_subtype(self, other, seen, indent=0):
        if isinstance(self, AnyType) or isinstance(other, AnyType):
            return True
        if self in seen:
            return True
        seen.add(self)
        # Allows extra keys in the other, but must have at least all the expected keys/values
        if type(self) == type(other) or any(parent.is_subtype(other, seen, indent + 1) for parent in self.parents):
            return all(
                any(
                    self_key.is_subtype(other_key, seen.copy(), indent + 1)
                    and self_value.is_subtype(other_value, seen.copy(), indent + 1)
                    for other_key, other_value in other.element_types
                ) for self_key, self_value in self.element_types)
        return False

    def add_type_arguments(self, type_arguments):
        if len(type_arguments) != 2:
            return ImpossibleType()
        # Put the single tuple pair into a new list
        # DictType has a list of pairs, representing possible mappings
        self.element_types = [type_arguments]
        return self

    def index(self, key):
        # TODO: Support a flag for whether Numbers are allowed for Integers
        if self.is_empty:
            return ImpossibleType()
        return self._find_best_item(key)[2] or ImpossibleType()

    def allows_membership(self, key):
        return any(is_subtype(key, potential_key) for potential_key, value in self.element_types)

    def iterate(self):
        keys = [k for k, v in self.element_types]
        if len(keys) == 0:
            return AnyType()
        elif len(keys) == 1:
            return keys[0]
        else:
            potential = widest_type(keys)
            if potential:
                return potential
            return TypeUnion(keys)

    def break_apart(self):
        for key, value in self.element_types:
            yield key
        while True:
            yield ImpossibleType()

    def set_index(self, key, value_type):
        candidate = self._find_best_item(key)
        if candidate[0] is None:
            self.element_types.append((key, value_type))
        else:
            if isinstance(key, LiteralValue):
                if isinstance(candidate[1], LiteralValue):
                    if key.value == candidate[1].value:
                        self.element_types[candidate[0]] = candidate[1:]
                self.element_types.append((key, value_type))
            else:
                self.element_types[candidate[0]] = (widen_type(key, candidate[1]),
                                                    widen_type(value_type, candidate[2]))

    def as_type(self, tifa=None, location=None):
        return DictType([(k.as_type(tifa, location), v.as_type(tifa, location))
                         for k, v in self.element_types])

    @staticmethod
    def keys(tifa, function, callee, arguments, named_arguments, location):
        self_type = function.the_self
        if self_type.is_empty:
            return GeneratorType(True)
        return GeneratorType(False, widest_type([key for key, value in self_type.element_types]))

    @staticmethod
    def values(tifa, function, callee, arguments, named_arguments, location):
        self_type = function.the_self
        if self_type.is_empty:
            return GeneratorType(True)
        return GeneratorType(False, widest_type([value for key, value in self_type.element_types]))

    @staticmethod
    def items(tifa, function, callee, arguments, named_arguments, location):
        self_type = function.the_self
        if self_type.is_empty:
            return GeneratorType(True)
        keys, values = [], []
        for key, value in self_type.element_types:
            keys.append(key)
            values.append(value)
        return GeneratorType(False, TupleType([widest_type(keys), widest_type(values)]))

    @staticmethod
    def get(tifa, function, callee, arguments, named_arguments, location):
        self_type = function.the_self
        if not arguments:
            return ImpossibleType()
        return self_type._find_best_item(arguments[0])[1] or NoneType()

    @staticmethod
    def copy(tifa, function, callee, arguments, named_arguments, location):
        return function.the_self.clone()

    pop = get

    # TODO: popitem, setdefault, update


class ClassType(Type):
    name = "Class"
    singular_name = "a class"
    plural_name = "classes"
    immutable = False
    fields = {}
    parents = []

    def __init__(self, name, fields=None, parents=None):
        super().__init__()
        self.name = name
        self.fields = fields if fields is not None else {}
        self.parents = parents if parents is not None else []

    @property
    def singular_name(self):
        return f"a {self.name} class"

    @property
    def plural_name(self):
        return f"{self.name} classes"

    def __str__(self):
        return f"ClassType[{self.name}]"

    def get_constructor(self):
        """ We actually follow the true constructor/initializer separation here!"""
        # Default constructor
        def constructor(*args):
            return InstanceType(self)

        return FunctionType(name='__init__', definition=constructor)

    def clone(self):
        return ClassType(self.name, self.fields.copy(), self.parents().copy())

    def is_subtype(self, other, seen, indent=0):
        if isinstance(self, AnyType) or isinstance(other, AnyType):
            return True
        if self in seen:
            return True
        seen.add(self)
        if other == TYPE_TYPE or self == other:
            return True
        return any(parent.is_subtype(other, seen, 1+indent) for parent in self.parents)

    def as_type(self, tifa=None, location=None):
        return InstanceType(self)


class BuiltinConstructorType(Type):
    name = "type"
    immutable = True
    fields = {}
    parents = []
    type_arguments: tuple  # type: tuple[Type]

    def __init__(self, name=None, type_arguments=None):
        super().__init__()
        if name is not None:
            self.name = name
        self.type_arguments = type_arguments

    def clone(self):
        return self.__class__(self.name, self.type_arguments)

    @property
    def singular_name(self):
        return f'the {self.name} constructor function'

    @property
    def plural_name(self):
        return f'{self.name} constructor functions'

    def index(self, key):
        self.type_arguments = key
        return self

    def definition(self, tifa, function, callee, arguments, named_arguments, location):
        return AnyType()

    def as_type(self, tifa=None, location=None):
        return self.definition(tifa, self, None, [], [], location)

    def add_type_arguments(self, type_arguments):
        if isinstance(type_arguments, (tuple, list)):
            self.type_arguments = type_arguments[0] if len(type_arguments) == 1 else TupleType(type_arguments)
        else:
            self.type_arguments = type_arguments
        return self

class IntConstructor(BuiltinConstructorType):
    name = 'int'
    definition = lambda *args: IntType()


class FloatConstructor(BuiltinConstructorType):
    name = 'float'
    definition = lambda *args: FloatType()


class BoolConstructor(BuiltinConstructorType):
    name = 'bool'
    definition = lambda *args: BoolType()


class StrConstructor(BuiltinConstructorType):
    name = 'str'

    def definition(self, tifa, function, callee, arguments, named_arguments, location):
        if arguments:
            if is_subtype(arguments[0], StrType()):
                return arguments[0].clone()
            return StrType(False)
        return StrType(True)


class ElementContainerConstructor(BuiltinConstructorType):
    element_container_type: type(ElementContainerType)

    def definition(self, tifa, function, callee, arguments, named_arguments, location):
        element_type = self.type_arguments
        #if isinstance(element_type, BuiltinConstructorType):
        #    element_type = element_type.definition(self, element_type, None, [], [], location)
        if element_type is None:
            element_type = AnyType()
        element_type = element_type.as_type(tifa, location)
        result_type = self.element_container_type(bool(arguments), element_type)
        if arguments:
            result_type = specify_subtype(result_type, arguments[0].iterate())
        return result_type


class ListConstructor(ElementContainerConstructor):
    name = 'list'
    element_container_type = ListType


class SetConstructor(ElementContainerConstructor):
    name = 'set'
    element_container_type = SetType


class FrozenSetConstructor(ElementContainerConstructor):
    name = 'frozenset'
    element_container_type = FrozenSetType


class DictConstructor(BuiltinConstructorType):
    name = 'dict'

    def definition(self, tifa, function, callee, arguments, named_arguments, location):
        element_type = self.type_arguments
        if element_type is None:
            element_type = AnyType()
        key_type, value_type = element_type.index(LiteralInt(0)), element_type.index(LiteralInt(1))
        if isinstance(key_type, BuiltinConstructorType):
            key_type = key_type.definition(self, key_type, None, [], [], location)
        if isinstance(value_type, BuiltinConstructorType):
            value_type = value_type.definition(self, value_type, None, [], [], location)
        if arguments:
            # TODO: Parse the argument for more data!
            return DictType([(key_type, value_type)])
        return DictType([(key_type, value_type)])


class TupleConstructor(BuiltinConstructorType):
    name = 'tuple'

    def definition(self, tifa, function, callee, arguments, named_arguments, location):
        element_type = self.type_arguments
        if element_type is None:
            # TODO: How do we handle completely generic tuples?
            # For now, we'll treat them as if they were empty tuples...
            return TupleType([])
        # Assume single elements are actually just a tuple of length one
        if not isinstance(element_type, (tuple, set, list)):
            element_type = [element_type]
        element_type = [e.definition(self, e, None, [], [], location)
                        for e in element_type if isinstance(e, BuiltinConstructorType)]
        result_type = TupleType(element_type)
        if arguments:
            result_type = specify_subtype(result_type, arguments[0])
        return result_type


TYPE_TYPE = BuiltinConstructorType("type")


class InstanceType(Type):
    immutable = False
    fields = {}

    def __init__(self, parent):
        super().__init__()
        self.parents = [parent]
        self.fields = {}
        self.name = parent.name

    def __str__(self):
        return "InstanceTypeOf" + str(self.parents[0].name)

    @property
    def singular_name(self):
        return add_indefinite_article(self.name)

    @property
    def plural_name(self):
        return self.name

    def clone(self):
        return InstanceType(self.parents[0])

    def is_subtype(self, other, seen, indent=0):
        if isinstance(self, AnyType) or isinstance(other, AnyType):
            return True
        # Avoid recursion
        if self in seen:
            return True
        seen.add(self)
        # Check that the structure matches the expected
        if type(self) == type(other) and other.name == self.name:
            for expected_field_name in set(other.list_fields()):
                if expected_field_name.startswith('__'):
                    continue
                expected_field_type = other.find_field(expected_field_name, set())
                actual_field_type = self.find_field(expected_field_name, set())
                if actual_field_type is None or expected_field_type is None:
                    return False
                if not is_subtype(actual_field_type, expected_field_type):
                    return False
            return True

        def check_parent(current):
            if isinstance(current, AnyType):
                return True
            if current.name == other.name:
                return True
            if current in seen:
                return True
            seen.add(self)
            return any(check_parent(parent) for parent in current.parents)
        result = any(check_parent(parent) for parent in self.parents)
        return result

    def add_attr(self, field: str, value):
        if field in self.fields:
            if not is_subtype(self.fields[field], value):
                return ImpossibleType()
        self.fields[field] = value
        return value


def make_dataclass(tifa, function, callee, arguments, named_arguments: dict, location):
    class_type = arguments[0]
    simple_class_fields = [(field, expected_type) for field, expected_type in class_type.fields.items()
                           if not isinstance(expected_type, FunctionType)]

    def constructor(tifa, function, callee, arguments, named_arguments: dict, location):
        seen_fields = set()
        missing_fields = []
        arguments = arguments.copy()
        the_self = arguments.pop(0) if arguments else None
        named_arguments = named_arguments.copy()
        new_instance = InstanceType(class_type)
        # TODO: Handle kwargs better
        kwargs = [(k, v) for k, v in named_arguments if k is None]
        for field, expected_type in simple_class_fields:
            # Key is found?
            # Key's value has right type?
            if field in named_arguments:
                value = named_arguments.pop(field)
            elif field in kwargs:
                value = kwargs.pop(field)
            elif arguments:
                value = arguments.pop(0)
            else:
                #tifa._issue('missing_parameter', location, field, expected_type)
                missing_fields.append((field, expected_type))
                continue
            seen_fields.add(field)
            if not is_subtype(value, expected_type):
                tifa._issue('field_type_mismatch', location, field, expected_type, value)
            new_instance.add_attr(field, value.clone_mutably())
        expected_field_count = len(simple_class_fields)
        actual_field_count = len(seen_fields) + len(arguments) + len(named_arguments) + len(kwargs)
        if expected_field_count != actual_field_count:
            # TODO: unexpected_dataclass_parameters
            tifa._issue('incorrect_arity', location, class_type.name, expected_field_count, actual_field_count, True)
        return new_instance
    constructor_function_type = FunctionType('__init__', definition=constructor)
    class_type.add_attr('__init__', constructor_function_type)
    return class_type


class ModuleType(Type):
    name = "Module"
    singular_name = "a module"
    plural_name = "modules"
    immutable = False
    fields = {}
    parents = []
    submodules: dict

    redefines: Set[str]

    def __init__(self, name, fields, submodules=None, redefines=None):
        super().__init__()
        self.name = name
        self.fields = fields
        self.submodules = submodules if submodules is not None else {}
        self.redefines = set(redefines) if redefines is not None else set()

    def clone(self):
        """ Create a copy of this ModuleType """
        submodules = {n: v.clone() for n, v in self.submodules.items()}
        fields = {n: v.clone() for n, v in self.fields.items()}
        return ModuleType(name=self.name, submodules=submodules, fields=fields)

    def shallow_clone(self):
        return ModuleType(name=self.name, submodules=self.submodules, fields=self.fields)

    def as_type(self, tifa=None, location=None):
        return ModuleType(name=self.name, submodules=self.submodules, fields={
            f: t.as_type(tifa, location) for f, t in self.fields.items()
        })


class FileType(Type):
    name = "FileType"
    singular_name = "a file"
    plural_name = "files"
    immutable = False
    fields = {}
    parents = []

    def iterate(self):
        return StrType()

    def break_apart(self):
        while True:
            yield StrType()


# TODO: Implement args/kwargs signature checking

NumType.fields = {
    # TODO: Finish these
    "as_integer_ratio": FunctionType("as_integer_ratio", returns=lambda: TupleType((IntType(), IntType())))
}

BoolType.fields = IntType.fields = {
    # TODO: Finish these
    "bit_length": FunctionType("bit_length", definition=IntType)
}

FloatType.fields = {
    "is_integer": FunctionType("is_integer", returns=BoolType)
}

StrType.fields = {
    # Methods that return strings
    "capitalize": FunctionType('capitalize', returns=StrType),
    "center": FunctionType(name='center', returns=StrType),
    "expandtabs": FunctionType(name='expandtabs', returns=StrType),
    "join": FunctionType(name='join', returns=StrType),
    "ljust": FunctionType(name='ljust', returns=StrType),
    "lower": FunctionType(name='lower', returns=StrType),
    "lstrip": FunctionType(name='lstrip', returns=StrType),
    "replace": FunctionType(name='replace', returns=StrType),
    "rjust": FunctionType(name='rjust', returns=StrType),
    "rstrip": FunctionType(name='rstrip', returns=StrType),
    "strip": FunctionType(name='strip', returns=StrType),
    "swapcase": FunctionType(name='swapcase', returns=StrType),
    "title": FunctionType(name='title', returns=StrType),
    "translate": FunctionType(name='translate', returns=StrType),
    "upper": FunctionType(name='upper', returns=StrType),
    "zfill": FunctionType(name='zfill', returns=StrType),
    # Methods that return numbers
    "count": FunctionType(name='count', returns=NumType),
    "find": FunctionType(name='find', returns=NumType),
    "rfind": FunctionType(name='rfind', returns=NumType),
    "index": FunctionType(name='index', returns=NumType),
    "rindex": FunctionType(name='rindex', returns=NumType),
    # Methods that return booleans
    "startswith": FunctionType(name='startswith', returns=BoolType),
    "endswith": FunctionType(name='endswith', returns=BoolType),
    "isalnum": FunctionType(name='isalnum', returns=BoolType),
    "isalpha": FunctionType(name='isalpha', returns=BoolType),
    "isdigit": FunctionType(name='isdigit', returns=BoolType),
    "islower": FunctionType(name='islower', returns=BoolType),
    "isspace": FunctionType(name='isspace', returns=BoolType),
    "istitle": FunctionType(name='istitle', returns=BoolType),
    "isupper": FunctionType(name='isupper', returns=BoolType),
    # Methods that return List of Strings
    "rsplit": FunctionType(name='rsplit', returns=lambda: ListType(False, StrType())),
    "split": FunctionType(name='split', returns=lambda: ListType(False, StrType())),
    "splitlines": FunctionType(name='splitlines', returns=lambda: ListType(False, StrType()))
}

SetType.fields = {
    "add": FunctionType("add", definition=SetType.add)
}

ListType.fields = {
    "append": FunctionType("append", definition=ListType.append),
}

TupleType.fields = {
    "count": FunctionType("count", returns=IntType),
    "index": FunctionType("index", returns=IntType)
}

DictType.fields = {
    'items': FunctionType('items', DictType.items),
    'keys': FunctionType('keys', DictType.keys),
    'values': FunctionType('values', DictType.values),
    'get': FunctionType('get', DictType.get),
    'copy': FunctionType('copy', DictType.copy),
    'pop': FunctionType('pop', DictType.pop),
    # TODO: Finish these
    # 'popitem': FunctionType('popitem', DictType.popitem),
    # 'setdefault': FunctionType('setdefault', DictType.setdefault),
    # 'update': FunctionType('update', DictType.update),
}

FileType.fields = {
    'close': FunctionType('close', definition=void_definition),
    'read': FunctionType('read', returns=StrType),
    'readline': FunctionType('readline', returns=StrType),
    'readlines': FunctionType('readlines', returns=lambda: ListType(False, StrType())),
    'write': FunctionType('write', returns=IntType),
    'writelines': FunctionType('writelines', returns=IntType),
    'tell': FunctionType('tell', returns=IntType),
    'seek': FunctionType('seek', returns=IntType),
}


class LiteralValue:
    """
    Special class flag that can be used to check if the type was defined as a literal.
    """
    value: any
    parents: list

    def __init__(self, value):
        self.value = value

    def promote(self):
        return self.parents[0]

    def clone(self):
        return self.__class__(self.value)


class LiteralBool(LiteralValue, BoolType):
    value: str
    singular_name = "a boolean"
    plural_name = "booleans"
    fields = {}
    parents = [BoolType()]


class LiteralStr(LiteralValue, StrType):
    value: str
    singular_name = "a string"
    plural_name = "strings"
    fields = {}

    @property
    def parents(self):
        return [StrType(self.is_empty)]

    def promote(self):
        return StrType(self.is_empty)


class LiteralInt(LiteralValue, Type):
    name = "LiteralInteger"
    singular_name = "an integer"
    plural_name = "integers"
    immutable = True
    value: int
    fields = {}
    parents = [IntType()]

    def __str__(self):
        return f"LiteralInteger[{self.value}]"


class LiteralFloat(LiteralValue, Type):
    name = "LiteralFloat"
    singular_name = "a float"
    plural_name = "floats"
    immutable = True
    value: int
    fields = {}
    parents = [FloatType()]

    def __str__(self):
        return f"LiteralFloat[{self.value}]"


# Types that support ordering
NUMERIC_TYPES = frozenset([
    NumType, IntType, FloatType, BoolType, LiteralInt, LiteralFloat
])
NumType.orderable = IntType.orderable = FloatType.orderable = BoolType.orderable = NUMERIC_TYPES
LiteralInt.orderable = LiteralFloat.orderable = NUMERIC_TYPES
StrType.orderable = LiteralStr.orderable = frozenset([StrType, LiteralStr])

for self_orderable in [ListType, SetType, TupleType]:
    self_orderable.orderable = frozenset([self_orderable])

TYPE_STRINGS = {
    "str": StrType, "string": StrType,
    "num": NumType, "number": NumType,
    "int": IntType, "integer": NumType, "float": FloatType,
    "complex": NumType,
    "bool": BoolType, "boolean": BoolType,
    "none": NoneType, "nonetype": NoneType,
    "dict": DictConstructor,
    "dictionary": DictConstructor,
    "list": ListConstructor,
    "tuple": TupleConstructor,
    "set": SetConstructor,
    "file": FileType,
    "func": FunctionType, "function": FunctionType,
    "class": ClassType,
}

STANDARD_NAMES = [
    "str", "int", "float", "complex", "num",
    "bool", "none", "dict", "list", "tuple", "set"
]


""" TOBEDEPRECATED: legacy support for using NumType and other similar names """
PEDAL_TYPE_NAMES = {
    "NumType": NumType,
    "StrType": StrType,
    "BoolType": BoolType,
    "ListType": ListType,
    "NoneType": NoneType
}


def exception_function(name):
    return FunctionType(name, returns=ExceptionType)


def int_function(name):
    return FunctionType(name, returns=IntType)


def float_function(name):
    return FunctionType(name, returns=FloatType)


def num_function(name):
    return FunctionType(name, returns=NumType)


def bool_function(name):
    return FunctionType(name, returns=BoolType)


def void_function(name):
    return FunctionType(name, void_definition)


def str_function(name):
    return FunctionType(name, returns=StrType)


def is_subtype(left, right):
    if left is None or right is None:
        return False
    else:
        return left.is_subtype(right, seen=set())


def specify_subtype(specific_type, receiving_type):
    if specific_type is None or receiving_type is None:
        return None
    return specific_type.specify_subtype(receiving_type)


def widen_type(left, right):
    if is_subtype(right, left) and not is_subtype(left, right):
        return left
    elif is_subtype(left, right):
        return right
    else:
        return None


def widest_type(type_values):
    if not type_values:
        return
    first_type = type_values[0]
    for type_value in type_values[1:]:
        first_type = widen_type(first_type, type_value)
        if first_type is None:
            return
    return first_type


if __name__ == "__main__":
    # Test cases
    "Complex Subtypes"
    list_of_list_of_integers = ListType(False, ListType(False, IntType()))
    list_of_list_of_numbers = ListType(False, ListType(False, NumType()))
    list_of_integers = ListType(False, IntType())
    assert not is_subtype(LiteralInt(5), list_of_integers)
    assert is_subtype(ListType(True), list_of_list_of_integers)
    assert is_subtype(ListType(False, ListType(True)), list_of_list_of_integers)
    assert is_subtype(ListType(False, ListType(False, IntType())), list_of_list_of_integers)
    assert not is_subtype(ListType(False, ListType(False, NumType())), list_of_list_of_integers)
    assert is_subtype(ListType(False, ListType(False, IntType())), list_of_list_of_numbers)
    assert is_subtype(ListType(False, ListType(False, LiteralInt(5))), list_of_list_of_integers)
    assert not is_subtype(IntType(), list_of_list_of_integers)
    assert not is_subtype(IntType(), list_of_list_of_numbers)
    assert not is_subtype(NumType(), list_of_list_of_integers)
    assert not is_subtype(NumType(), list_of_list_of_numbers)
    assert not is_subtype(ListType(False, IntType()), list_of_list_of_integers)
    assert not is_subtype(ListType(False, NumType()), list_of_list_of_integers)
    print(list_of_list_of_integers, list_of_list_of_integers.singular_name)
    xyz_coordinates = TupleType((IntType, IntType, IntType))
    print(xyz_coordinates, xyz_coordinates.singular_name)
    list_of_xyz_coordinates = ListType(False, xyz_coordinates)
    print(list_of_xyz_coordinates, list_of_xyz_coordinates.singular_name)

    "Instances and Classes"
    Animal = ClassType("Animal")
    Dog = ClassType("Dog", parents=[Animal])
    Dog.add_attr("age", IntType())
    Dog.add_attr("fuzzy", BoolType())
    Dog.add_attr("name", StrType())
    dog_instances = Dog.get_constructor().definition()
    print(dog_instances)
    for field in ['name', 'age', 'fuzzy', 'is_pretty']:
        print("  ", field+":", dog_instances.get_attr(field))

    assert is_subtype(Dog, Dog), "Dogs are Dogs"

    "List of Instances"
    list_of_dog_instances = ListType(False, dog_instances)
    list_of_dogs = ListType(False, Dog)
    list_of_cats = ListType(False, ClassType("Cat"))
    list_of_animals = ListType(False, Animal)
    list_of_integers = ListType(False, IntType())
    assert is_subtype(list_of_dogs, ListType(False, TYPE_TYPE)), "Dog types are instances of Type Type"
    assert is_subtype(list_of_dog_instances, list_of_dogs), "Instances are subtypes of dogs"
    assert is_subtype(list_of_dog_instances, list_of_dog_instances), "Instances are subtypes of instances"
    assert is_subtype(list_of_dogs, list_of_dogs), "Dogs are not subtypes of dogs"
    assert not is_subtype(list_of_dog_instances, list_of_cats), "Instances of dogs are not subtypes of cats"
    assert is_subtype(list_of_dog_instances, list_of_animals), "Instances of dogs are subtypes of animals"
    assert not is_subtype(list_of_integers, list_of_animals), "Integers are not subtypes of animals"
    assert not is_subtype(StrType(), ClassType("Dog")), "Strings are not dogs"

    # Type widening
    assert type(widen_type(IntType(), LiteralInt(5))) == IntType
    assert type(widen_type(LiteralInt(3), IntType())) == IntType
    assert type(widen_type(NumType(), LiteralInt(5))) == NumType
    assert type(widen_type(LiteralInt(3), NumType())) == NumType
    assert type(widen_type(NumType(), IntType())) == NumType
    assert type(widen_type(IntType(), NumType())) == NumType
    assert widen_type(LiteralInt(3), StrType()) is None
    assert widen_type(StrType(), LiteralInt(3)) is None
    assert widen_type(dog_instances, Dog) == Dog
    assert widen_type(Dog, dog_instances) == Dog



    print("All good!")


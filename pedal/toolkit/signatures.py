import re

from pedal.cait.cait_api import parse_program
from pedal.report.imperative import gently, explain

"""
Verify indentation

Format:


Any number of text. One final newline separates the next section.

If line is "Args:" or "Returns:"
    Next line will be a "param (type): Description" or "type: Description"
    If the next line is indented more than current level, then it is part of the previous part's description.
    Otherwise, new entry

"Note:"
    Any level of indentation indicates
"""

PRIMITIVES = {
    'text': ['text'],
    'str': ['string', 'str', 'unicode'],
    'bytes': ['bytes'],
    'io': ['io'],
    'file': ['file'],
    'num': ['number', 'num', 'numeric'],
    'int': ['int', 'integer'],
    'float': ['float', 'floating'],
    'bool': ['bool', 'boolean'],
    'none': ['none'],
    'any': ['any']
}
NORMALIZE_PRIMITIVES = {synonym: formal
                        for formal, synonyms in PRIMITIVES.items()
                        for synonym in synonyms}
CONTAINERS = {
    'list': (1, ['list']),
    'set': (1, ['set']),
    'optional': (1, ['optional', 'maybe']),
    'dict': (2, ['dict', 'dictionary']),
    'callable': (2, ['callable', 'function', 'func']),
    'union': ('*', ['union', 'itemization']),
    'tuple': ('*', ['tuple', 'pair']),
}
NORMALIZE_CONTAINERS = {synonym: formal
                        for formal, (length, synonyms) in CONTAINERS.items()
                        for synonym in synonyms}

INHERITANCE = {
    'int': 'num',
    'float': 'num',
    'bool': 'num',
    'str': 'text',
    'bytes': 'text',
    'list': 'iterable',
    'tuple': 'iterable',
    'set': 'iterable',
    'dict': 'iterable',
    'file': 'iterable',
    'text': 'iterable'
}

SPECIAL_PARAMETERS = ["_returns", "yields", "prints", "_raises",
                      "_report", "_root"]

'''
Type validation:
    Caps does not matter
    Primitives:
    Containers
    Unions
        X or Y
        X, Y, or Z
        X, Y, Z
    Function
        (X -> Y)
    
    list[int, str, or bool], dict[int: str], or bool or int
'''


class SignatureException(Exception):
    pass


class Stack:
    def __init__(self, identifier="union"):
        self.body = []
        self.identifier = identifier

    def append(self, value):
        self.body.append(value)

    def __repr__(self):
        return "{}[{}]".format(self.identifier, ", ".join(map(repr, self.body)))

    def __hash__(self):
        return hash(tuple(self.identifier, self.body))

    def __lt__(self, other):
        if isinstance(other, Stack):
            return self.identifier < other.identifier and self.body < other.body
        return self.identifier < other

    def __gt__(self, other):
        if isinstance(other, Stack):
            return self.identifier > other.identifier and self.body > other.body
        return self.identifier > other

    def __eq__(self, other):
        if isinstance(other, Stack):
            return self.identifier == other.identifier and self.body == other.body
        return False


def _normalize_identifier(identifier):
    if identifier in NORMALIZE_PRIMITIVES:
        return NORMALIZE_PRIMITIVES[identifier]
    elif identifier in NORMALIZE_CONTAINERS:
        return NORMALIZE_CONTAINERS[identifier]
    else:
        return identifier


SPECIAL_SYMBOLS = r"\s*(->|\s*[\[\],\(\)\:]|or)\s*"


def _parse_tokens(tokens):
    result_stack = [Stack()]
    tokens = list(reversed(list(tokens)))
    while tokens:
        current = tokens.pop()
        # Ending a parenthetical, better stop here.
        if current == ")":
            subexpression = result_stack.pop()
            result_stack[-1].append(subexpression)
        # Ending a square bracket, better stop here.
        elif current == "]":
            subexpression = result_stack.pop()
            result_stack[-1].append(subexpression)
        # We've reached the last token!
        elif not tokens:
            # And had no tokens before this one
            # Return the set of tokens
            result_stack[-1].append(_normalize_identifier(current))
        # Starting a parentheized expression
        elif current == "(":
            result_stack.append(Stack())
        # Nullary function
        elif current == "->":
            result_stack[-1].append(Stack("callable"))
        elif current in ("or", ",", ":"):
            pass
        else:
            next = tokens.pop()
            # X or ...
            if current == "," and next == "or":
                tokens.append(next)
            if next in ("or", ",", "->", ":"):
                result_stack[-1].append(_normalize_identifier(current))
            # X [ ...
            elif next == "[":
                result_stack.append(Stack(_normalize_identifier(current)))
            else:
                tokens.append(next)
                result_stack[-1].append(_normalize_identifier(current))
    return result_stack.pop()


def sort_stacks(s):
    if isinstance(s, Stack):
        return (True, (s.identifier, s.body))
    return (False, s)


def normalize_type(t):
    t = t.strip()
    tokens = re.split(SPECIAL_SYMBOLS, t)
    tokens = [token for token in tokens if token]
    parsed = _parse_tokens(tokens)
    return parsed


def check_piece(left, right, indent=1):
    if type(left) != type(right):
        return False
    elif isinstance(left, Stack):
        if left.identifier != right.identifier:
            return False
        elif len(left.body) != len(right.body):
            return False
        elif left.identifier == "union":
            # Handle them in any order
            left.body.sort(key=sort_stacks)
            right.body.sort(key=sort_stacks)
        # Match them in exact order
        for l, r in zip(left.body, right.body):
            if not check_piece(l, r, indent=indent + 1):
                return False
        return True
    else:
        return left == right


def type_check(left, right):
    left = normalize_type(left)
    right = normalize_type(right)
    return check_piece(left, right)
    
def find_colon(str):
    parens_stack = []
    for i, character in enumerate(str):
        if character in '[(':
            parens_stack.append(character)
        elif character in '])':
            parens_stack.pop()
        elif character == ':' and not parens_stack:
            return i
    return 0
    
ARGS = ('args:', 'arg:', 'argument:', 'arguments:',
        'parameters:', 'params:', 'parameter:', 'param:')
ARG_PATTERN = r'(.+)\s*\((.+)\)\s*:(.+)'
RETURNS = ('returns:', 'return:')
def parse_docstring(doc):
    # First line's indentation may be different from rest - trust first
    # non empty line after the first one.
    # Remove taht number of spaces from subsequent lines
    # If Line is "Args:" or other special...
    # 
    lines = doc.split("\n")
    body = [lines[0]]
    args = {}
    current_arg = None
    returns = []
    current_component = 'body'
    indentation = None
    inner_indentation = None
    for line in lines[1:]:
        # Blank line, not interesting!
        if not line.strip():
            continue
        # Get the actual text
        if indentation is None:
            indentation = len(line) - len(line.lstrip())
        line = line[indentation:]
        potential_command = line.lower().strip()
        # New command region?
        if potential_command in ARGS:
            current_component = 'args'
            inner_indentation = None
            continue
        elif potential_command in RETURNS:
            current_component = 'returns'
            inner_indentation = None
            continue
        # Okay, it's content - let's process it
        if current_component == 'body':
            body.append(line)
        else:
            if inner_indentation is None:
                inner_indentation = len(line) - len(line.lstrip())
            line = line[inner_indentation:]
            # Skip indented lines
            if not re.match(r'\s', line):
                if current_component == 'args':
                    match = re.search(ARG_PATTERN, line)
                    current_arg = match.group(1)
                    type_str = match.group(2)
                    args[current_arg.strip()] = type_str.strip()
                elif current_component == 'returns':
                    position = find_colon(line)
                    return_type, comment = line[:position], line[position:]
                    returns.append(return_type.strip())
    return body, args, ' or '.join(returns)

def function_signature(function_name, returns=None, yields=None,
                       prints=None, raises=None, report=None, root=None,
                       **kwargs):
    """
    Determines whether the function with this signature is in the AST.
    
    TODO: Implement raises, prints, yields
    """
    if root is None:
        root = parse_program()
    # If you encounter any special parameters with a "_", then fix their
    # name. This allows for students to have parameters with the given name.
    for special_parameter in SPECIAL_PARAMETERS:
        if special_parameter in kwargs:
            kwargs[special_parameter[1:]] = kwargs.pop(special_parameter)
    # Go get the actual docstring, parse it
    docstring = None
    for function_def in root.find_all("FunctionDef"):
        if function_def._name == function_name:
            if function_def.body:
                if (function_def.body[0].ast_name == "Expr" and
                        function_def.body[0].value.ast_name == "Str"):
                    docstring = function_def.body[0].value.s
    # Try to match each element in turn.
    if docstring is None:
        return False

    try:
        body, args, parsed_returns = parse_docstring(docstring)
    except Exception as e:
        return [e], False
    failing_parameters = []
    for name, type in kwargs.items():
        if name in args:
            if not type_check(type, args[name]):
                failing_parameters.append(name)
        else:
            failing_parameters.append(name)
    if returns is None and not returns:
        return failing_parameters, True
    elif returns is not None and returns:
        return failing_parameters, type_check(parsed_returns, returns)
    else:
        return failing_parameters, False


def class_signature(class_name, report=None, root=None, **attributes):
    """

    Args:
        class_name:
        **attributes:
        report:
        root:

    Returns:

    """
    if root is None:
        root = parse_program()


"""

"""

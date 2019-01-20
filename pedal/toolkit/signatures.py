import re

from pedal.cait.cait_api import parse_program
from pedal.report.imperative import gently, explain

from pedal.toolkit.docstring import GoogleDocstring, dedent

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
        #print("\tCurrently:", result_stack)
        #print("\tChecking:", current, end="")
        # Ending a square bracket, better stop here.
        # Ending a parenthetical, better stop here.
        if current == ")":
            subexpression = result_stack.pop()
            result_stack[-1].append(subexpression)
            #print("- Ending a )")
        elif current == "]":
            subexpression = result_stack.pop()
            result_stack[-1].append(subexpression)
            #print("- Ending a ]")
        # We've reached the last token!
        elif not tokens:
            # And had no tokens before this one
            # Return the set of tokens
            result_stack[-1].append(_normalize_identifier(current))
            #print("- End of the line!")
        # Starting a parentheized expression
        elif current == "(":
            result_stack.append(Stack())
            #print("- Starting a (")
        # Nullary function
        elif current == "->":
            result_stack[-1].append(Stack("callable"))
            #print("- Nullary expression")
        elif current in ("or", ","):
            pass #print("- Lonely or")
        else:
            next = tokens.pop()
            # X or ...
            #print("^^", current, next, "^^")
            if current == "," and next == "or":
                tokens.append(next)
                #print("- Double Operator:", next)
            if next in ("or", ",", "->"):
                result_stack[-1].append(_normalize_identifier(current))
                #print("- Operator:", next, _normalize_identifier(current))
            # X [ ...
            elif next == "[":
                result_stack.append(Stack(_normalize_identifier(current)))
                #print("- Starting:", next, _normalize_identifier(current))
            else:
                tokens.append(next)
                result_stack[-1].append(_normalize_identifier(current))
                #print("- Just", _normalize_identifier(current))
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
            if not check_piece(l, r, indent=indent+1):
                return False
        return True
    else:
        return left == right
                      
def type_check(left, right):
    left = normalize_type(left)
    right = normalize_type(right)
    return check_piece(left, right)


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
        if function_def.name == function_name:
            if function_def.body:
                if (function_def.body[0].ast_name == "Expr" and
                    function_def.body[0].value.ast_name == "Str"):
                    docstring = function_def.body[0].value.s
    # Try to match each element in turn.
    if docstring is None:
        return False
    class Config:
        napoleon_use_param=True
        napoleon_use_rtype=True
        napoleon_custom_sections=[]
    docstring = dedent(docstring)
    docstring = GoogleDocstring(docstring, Config(), what='function', name=function_name)
    failing_parameters = []
    for name, type, description in docstring.parsed_parameters:
        if name in kwargs:
            if not type_check(type, kwargs[name]):
                failing_parameters.append(name)
    if returns is not None:
        return failing_parameters, type_check(docstring.parsed_returns, returns)
    else:
        return failing_parameters, True

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

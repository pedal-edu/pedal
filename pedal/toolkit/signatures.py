from pedal.cait.cait_api import parse_program
from pedal.report.imperative import gently, explain

'''
Verify indentation

Format:


Any number of text. One final newline separates the next section.

If line is "Args:" or "Returns:"
    Next line will be a "param (type): Description" or "type: Description"
    If the next line is indented more than current level, then it is part of the previous part's description.
    Otherwise, new entry

"Note:"
    Any level of indentation indicates
    
Type validation:
    Caps does not matter
    Primitives:
        string, str, text
        number, num, numeric
            int, integer
            float, floating
        bool, boolean
        none
    Unions
        X or Y
    Parameterized
        list
        list[X]
        dict[X:Y]
        tuple[X:Y]
    Custom classes
        Person
'''

SPECIAL_PARAMETERS = ["_returns", "yields", "prints", "_raises", 
                      "_report", "_root"]
def function_signature(function_name, returns=None, yields=None,
                       prints=None, raises=None, report=None, root=None,
                       **kwargs):
    '''
    
    '''
    if root is None:
        root = parse_program()
    # If you encounter any special parameters with a "_", then fix their
    # name. This allows for students to have parameters with the given name.
    for special_parameter in SPECIAL_PARAMETERS:
        if special_parameter in kwargs:
            kwargs[special_parameter[1:]] = kwargs.pop(special_parameter)
    # Go get the actual docstring, parse it
    # Try to match each element in turn.

def class_signature(class_name, **attributes, report=None, root=None):
    '''
    '''
    if root is None:
        root = parse_program()

'''
def find_string(needle, haystack):
    """
    Finds the given needle in the haystack.
    
    Args:
        haystack (list[str]): The list of strings to look within.
        needle (str): The given string to be searching for.
    Returns:
        bool: Whether the string is in the list.
    """

document_function("find_string", needle="str", haystack="list[str]", returns="bool")
'''
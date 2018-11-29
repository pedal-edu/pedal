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
        list of X, list
        dict of X:Y
        tuple of X:Y
    Custom classes
        Person
'''
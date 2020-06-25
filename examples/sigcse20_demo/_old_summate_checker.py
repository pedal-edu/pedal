from pedal.toolkit.utilities import prevent_builtin_usage
from pedal.environments.quick import *

code, student, resolve = setup_pedal()
match = find_match("def summate(): __expr__")
if match:
    if match['__expr__'].find_match("summate()"):
        explain("You are doing recursion, don't do that!", label="used_recursion")
    else:
        assertEqual(student.call('summate', [1, 3, 5]), 9)
else:
    explain("You have not defined the function", "function_missing")
prevent_builtin_usage('sum')
resolve()

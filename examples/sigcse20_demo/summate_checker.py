from pedal.environments.quick import *

setup_pedal()
student = run()

match = find_match("""
def summate():
    __expr__
""")
if not match:
    explain("You have not defined the function summate.", label="function_missing")
else:
    if match['__expr__'].find_match('summate()'):
        explain("You are doing recursion, don't do that.", label="used_recursion")
    else:
        assertEqual(student.call('summate', [1, 3, 5]), 9)

resolve()

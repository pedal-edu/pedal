from pedal import *

code = """# First line is up here
def add(a: int, b: int) -> int:
    return a + b
{1:3
add(5, 3)
"""

set_source(code)
verify()
run()

print_resolve()
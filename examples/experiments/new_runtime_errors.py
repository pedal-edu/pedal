from pedal import *

code = """# First line is up here
def alpha(x: int) -> int:
    y = beta(5 + 
    x)
    return y

def beta(z: int) -> int:
    return "" + z

print(alpha(3))
"""

set_source(code)
verify()
run()

print_resolve()
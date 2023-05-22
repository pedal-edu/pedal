import sys
from pedal import *

sys.stdout.write("Gimme value:")
#sys.stdout.flush()
print(sys.stdin.readline())


set_source("a = 'Give me a value: '\nprint(input(a))")

allow_real_io()
run()
print(get_output())

block_real_io()
run()
print(get_output())

allow_real_io()
run()
print(get_output())

print_resolve()
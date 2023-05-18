from pedal import *

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
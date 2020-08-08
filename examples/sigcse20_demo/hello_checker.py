from pedal.environments.quick import *

setup_pedal()

student = run()

assert_prints(student, "Hello world")

resolve()

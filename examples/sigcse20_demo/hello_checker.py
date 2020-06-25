from pedal.environments.quick import *

code, student, resolve = setup_pedal()

# if 'Hello world' not in student.output:
if not student.printed('Hello world'):
    gently("You have the wrong output", label="wrong_output")

resolve()

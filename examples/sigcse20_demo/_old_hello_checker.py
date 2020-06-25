from pedal.environments.quick import *

ast, student, resolve = setup_pedal()

# if not student.printed('Hello world'):
if 'Hello world' not in student.output:
    gently("You have the wrong output", label="wrong_output")

resolve()

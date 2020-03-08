from pedal import explain, set_success
from pedal.environments.standard import setup_pedal

ast, student, resolve = setup_pedal()

if student.output != ["Hello world!"]:
    explain("You need to print out 'Hello world!' exactly.", label="wrong_output")
else:
    set_success()

resolve()
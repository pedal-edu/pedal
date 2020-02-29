from pedal.environments.standard import StandardEnvironment

ast, student, resolve = StandardEnvironment()

import sys

from pedal import *

if student.output != ["Hello world!"]:
    explain("You need to print out 'Hello world!' exactly.", label="wrong_output")
else:
    set_success()

resolve()
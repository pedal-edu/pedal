"""
This file is meant to be an idealized example of Pedal with a completely generic autograding environment that
wants to do as little work as possible.
"""

from pedal.environments.quick import setup_pedal
from pedal.core.commands import set_success

ast, student, resolve = setup_pedal(main_code="print('Hello world!')")

if ast.find_all("Call"):
    set_success()

resolve()
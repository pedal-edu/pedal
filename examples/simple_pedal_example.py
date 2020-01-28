"""
This file is meant to be an idealized example of Pedal with a completely generic autograding environment that
wants to do as little work as possible.
"""

from pedal.environments.simple import SimpleEnvironment
from pedal.core.commands import set_success

environment = SimpleEnvironment("print('Hello world!')")
ast, student = environment.ast, environment.student

if ast.find_all("Call"):
    set_success()

environment.resolve()
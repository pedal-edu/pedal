from pedal.toolkit.utilities import prevent_builtin_usage
from pedal.quick import *

student, ast, resolve = setup_pedal()


prevent_builtin_usage('sum')

resolve()

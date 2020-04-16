from pedal.toolkit.utilities import prevent_builtin_usage
from pedal.quick import *

ast, student, resolve = setup_pedal()


prevent_builtin_usage('sum')

assertEqual(student.call('summate', [1, 2, 3]), 6)

resolve()

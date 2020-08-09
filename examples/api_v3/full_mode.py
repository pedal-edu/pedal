"""

$> python full_mode.py

"""

from pedal import *
from pedal.cait import find_match
from pedal.tifa import tifa_analysis
from pedal.resolvers import print_resolve

contextualize_report("a = 0\na+''")
verify()
tifa_analysis()
student = run()

match = find_match("a = __value__")
gently(f"I found the value: {match['__value__']}")

set_success()

print_resolve()
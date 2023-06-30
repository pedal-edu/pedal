from pedal import *
from pedal.environments.terminal import setup_environment

pedal = setup_environment(main_file='examples/api_v3/student_code.py')
student = pedal.student
# Start of per-assignment code

# End of per-assignment code
final = pedal.resolve()

# To capture logging:
#final.to_file('output.json')
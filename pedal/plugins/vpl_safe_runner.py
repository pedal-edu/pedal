from pedal import run
from pedal.plugins.vpl import find_file
import sys

if __name__ == "__main__":
    find_file(sys.argv[1] if len(sys.argv) > 1 else 'main.py')
    student = run(tracer_style='coverage', context=False)
    print(student.raw_output)
    if student.exception:
        print(student.exception_formatted, file=sys.stderr)

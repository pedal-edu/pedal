from pedal import run
from pedal import set_source_file
import sys

if __name__ == "__main__":
    set_source_file(sys.argv[1] if len(sys.argv) > 1 else 'main.py')
    student = run(context=False)
    print(student.raw_output)
    if student.exception:
        print(student.exception_formatted, file=sys.stderr)

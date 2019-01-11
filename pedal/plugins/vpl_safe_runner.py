from pedal import run
from pedal.plugins.vpl import find_file
import sys

if __name__ == "__main__":
    find_file(sys.argv[1] if len(sys.argv) > 1 else 'exam.py')
    student = run(raise_exceptions=True)
    print(student.raw_output)
    if student.exception:
        raise student.exception

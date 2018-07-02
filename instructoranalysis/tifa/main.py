import tifa
import sys
import os

if __name__ == '__main__':
    if len(sys.argv) > 1:
        for path in sys.argv[1:]:
            with open(path, 'r') as inp:
                source = inp.read()
            tifa.process_code(source, "__main__.py")
            print(tifa)

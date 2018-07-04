import tifa
import sys
import os
from pprint import pprint

if __name__ == '__main__':
    t = tifa.Tifa()
    r = t.process_code('l=[{"A": 5}, {"B": 3}]\nfor x in l:\n b=x["A"]')
    pprint(vars(r['top_level_variables']['l'].type.subtype))
    '''if len(sys.argv) > 1:
        for path in sys.argv[1:]:
            with open(path, 'r') as inp:
                source = inp.read()
            tifa.process_code(source, "__main__.py")
            print(tifa)
    '''
import unittest
import os
import sys
from textwrap import dedent

pedal_library = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, pedal_library)

from pedal.plugins.vpl import find_file, resolve

class TestVPL(unittest.TestCase):
    def test_vpl(self):
        find_file('tests/datafiles/student_example.py')
        

if __name__ == '__main__':
    unittest.main(buffer=False)
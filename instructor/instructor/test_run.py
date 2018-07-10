from run import run

import sys
import unittest

class TestCode(unittest.TestCase):
    def setUp(self):
        pass
        
    def test_normal_run(self):
        result = run('a=0\nprint(a)')
        self.assertIn('a', result.variables)
        self.assertEqual(result.variables['a'], 0)
        self.assertEqual(len(result.output), 1)
        self.assertIn('0', result.output[0])
    
    def test_input(self):
        result = run('b = input("Give me something:")\nprint(b)',
                     inputs=['Hello World!'])

if __name__ == '__main__':
    unittest.main(buffer=False)
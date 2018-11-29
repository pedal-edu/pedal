from textwrap import dedent
import unittest
from pprint import pprint
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pedal.sandbox import Sandbox
import pedal.sandbox.compatibility as compatibility
from pedal.source import set_source

class TestCode(unittest.TestCase):
    def setUp(self):
        pass
        
    def test_normal_run(self):
        student = Sandbox()
        student.run('a=0\nprint(a)')
        self.assertIn('a', student.data)
        self.assertEqual(student.data['a'], 0)
        self.assertEqual(len(student.output), 1)
        self.assertIn('0', student.output[0])
    
    def test_input(self):
        student = Sandbox()
        student.run('b = input("Give me something:")\nprint(b)',
                    _inputs=['Hello World!'])
        self.assertIn('b', student.data)
        self.assertEqual(student.data['b'], 'Hello World!')
                     
    def test_oo(self):
        # Load the "bank.py" code
        student_code = dedent('''
            class Bank:
                def __init__(self, balance):
                    self.balance = balance
                def save(self, amount):
                    self.balance += amount
                    return self.balance > 0
                def take(self, amount):
                    self.balance -= amount
                    return self.balance > 0''')
        student = Sandbox()
        student.run(student_code, _as_filename='bank.py')
        # Check that we created the class
        self.assertIn('Bank', student.data)
        # Now let's try making an instance
        student.call('Bank', 50, _target='bank')
        self.assertIsInstance(student.data['bank'], student.data['Bank'])
        # Can we save money?
        student.call('bank.save', 32)
        self.assertTrue(student._)
        # What about extracting money?
        student.data['bank'].balance += 100
        student.call('bank.take', 100)
        self.assertTrue(student._)
    
    def test_improved_exceptions(self):
        student_code = '0+"1"'
        student = Sandbox()
        student.run(student_code, _as_filename='student.py')
        self.assertIsNotNone(student.exception)
        self.assertIsInstance(student.exception, TypeError)
        self.assertEqual(student.exception_position, {'line': 1})
        
        self.assertEqual(student.format_exception(), 
"""
Traceback:
  File "student.py", line 1
TypeError: unsupported operand type(s) for +: 'int' and 'str'\n"""
        )
    
    def test_call(self):
        student_code = "def average(a,b):\n return (a+b)/2"
        student = Sandbox()
        student.run(student_code, _as_filename='student.py')
        student.call('average', 10, 12)
    
    def test_compatibility_api(self):
        student_code = 'word = input("Give me a word")\nprint(word+"!")'
        set_source(student_code)
        self.assertFalse(compatibility.get_output())
        compatibility.queue_input("Hello")
        self.assertIsNone(compatibility.run_student())
        self.assertEqual(compatibility.get_output(), 
                         ["Give me a word", "Hello!"])
        compatibility.queue_input("World", "Again")
        self.assertIsNone(compatibility.run_student())
        self.assertEqual(compatibility.get_output(), 
                         ["Give me a word", "Hello!", 
                          "Give me a word", "World!"])
        self.assertIsNone(compatibility.run_student())
        self.assertEqual(compatibility.get_output(),
                         ["Give me a word", "Hello!", 
                          "Give me a word", "World!", 
                          "Give me a word", "Again!"])
        compatibility.reset_output()
        compatibility.queue_input("Dogs", "Are", "Great")
        self.assertIsNone(compatibility.run_student())
        self.assertIsNone(compatibility.run_student())
        self.assertIsNone(compatibility.run_student())
        self.assertEqual(compatibility.get_output(), 
                         ["Give me a word", "Dogs!", 
                          "Give me a word", "Are!", 
                          "Give me a word", "Great!"])

    def test_compatibility_exceptions(self):
        student_code = '1 + "Banana"'
        set_source(student_code)
        exception = compatibility.run_student()
        self.assertIsNotNone(exception)
    
    def test_get_by_types(self):
        student_code = dedent('''
            my_int = 0
            my_other_int = 5
            my_str = "Hello there!"
            response_str = "General Kenobi!"
            a_list = [1,2,3]
            another_list = [4,5,6]
        ''')
        student = Sandbox()
        student.run(student_code, _as_filename='student.py')
        # ints
        ints = student.get_names_by_type(int)
        self.assertEqual(len(ints), 2)
        self.assertIn('my_int', ints)
        self.assertIn('my_other_int', ints)
        # lists
        lists = student.get_names_by_type(list)
        self.assertEqual(len(lists), 2)
        self.assertIn('a_list', lists)
        self.assertIn('another_list', lists)
        # strs
        strs = student.get_values_by_type(str)
        self.assertEqual(len(strs), 2)
        self.assertIn('Hello there!', strs)
        self.assertIn('General Kenobi!', strs)
    
    def test_matplotlib(self):
        student_code = dedent('''
            import matplotlib.pyplot as plt
            plt.plot([1,2,3])
            plt.title("My line plot")
            plt.show()
        ''')
        student = Sandbox()
        student.run(student_code, _as_filename='student.py')
        self.assertIn('matplotlib.pyplot', student.modules)
        plt = student.modules['matplotlib.pyplot']
        self.assertEqual(len(plt.plots), 1)
        
    def test_matplotlib_compatibility(self):
        student_code = dedent('''
            import matplotlib.pyplot as plt
            plt.plot([1,2,3])
            plt.title("My line plot")
            plt.show()
            plt.hist([1,2,3])
            plt.show()
        ''')
        set_source(student_code)
        exception = compatibility.run_student()
        plt2 = compatibility.get_plots()
        self.assertEqual(len(plt2), 2)
    
    def test_matplotlib_compatibility(self):
        student_code = dedent('''
            import os
            os
        ''')
        set_source(student_code)
        exception = compatibility.run_student()
        self.assertIsNone(exception)
    
    def test_coverage(self):
        student_code = dedent('''
            a = 0
            if True:
                print("Ran")
            else:
                print("Skipped")
            def x():
                b = 0
                return b
            print(a)
        ''')
        student = Sandbox()
        student.record_coverage = True
        student.run(student_code, _as_filename='student.py')
        self.assertTrue(student.coverage_report)
    
    def test_multiline_statements(self):
        student_code = dedent('''
            class X:
                def __init__(self, a, b):
                    self.a = a
                    self.b = b
                def update(self):
                    self.a += 10
        ''')
        # Need to be able to run several commands, any of which could fail
        #       needs to send out a nice stack trace in that case
        # We often want to assert the result of a call OR attribute OR other
        # data (type of attribute)
        # x = X(5, 10)
        # x.a == 5
        # x.b == 10
        # x.update()
        # x.a == 15
        

if __name__ == '__main__':
    unittest.main(buffer=False)

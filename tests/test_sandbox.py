from textwrap import dedent
import unittest
from pprint import pprint
import os
import sys
import json
import itertools

from pedal.core.submission import Submission

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pedal.core.commands import MAIN_REPORT, clear_report, contextualize_report
from pedal.sandbox import Sandbox, run
from pedal.sandbox.result import SandboxResult
import pedal.sandbox.commands as commands
from pedal.source import set_source
from pedal.utilities.system import IS_AT_LEAST_PYTHON_311, IS_AT_LEAST_PYTHON_310

here = "" if os.path.basename(os.getcwd()) == "tests" else "tests/"

class TestCode(unittest.TestCase):
    def setUp(self):
        """

        """
        pass

    def test_normal_run(self):
        student = Sandbox()
        student.run('a=0\nprint(a)', filename='student.py')
        self.assertIn('a', student.data)
        self.assertEqual(student.data['a'], 0)
        self.assertEqual(len(student.output), 1)
        self.assertIn('0', student.output[0])

    def test_input(self):
        student = Sandbox()
        student.run('b = input("Give me something:")\nprint(b)',
                    inputs=['Hello World!'])
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
        student.run(student_code, filename='bank.py')
        # Check that we created the class
        self.assertIn('Bank', student.data)
        # Now let's try making an instance
        student.call('Bank', 50, target='bank')
        self.assertIsInstance(student.data['bank'], student.data['Bank'])
        # Can we save money?
        student.call('bank.save', 32)
        self.assertTrue(student.result)
        # What about extracting money?
        student.data['bank'].balance += 100
        student.call('bank.take', 100)
        self.assertTrue(student.result)

    def test_improved_exceptions(self):
        TEST_FILENAME = here+'_sandbox_test_student.py'
        with open(TEST_FILENAME) as student_file:
            student_code = student_file.read()
        student = Sandbox()
        student.run(student_code, filename=TEST_FILENAME)
        self.assertIsNotNone(student.exception)
        self.assertIsInstance(student.exception, TypeError)
        self.assertEqual(1, student.feedback.location.line)
        self.assertEqual(dedent(
            """I ran the file _sandbox_test_student.py.

A TypeError occurred:

    Unsupported operand type(s) for +: 'int' and 'str'

The traceback was:
Line 1 of file _sandbox_test_student.py
    1+'0'
""" + ('    ^^^^^\n' if IS_AT_LEAST_PYTHON_311 else "") + """
Type errors occur when you use an operator or function on the wrong type of value. For example, using `+` to add to a list (instead of `.append`), or dividing a string by a number.

Suggestion: To fix a type error, you should trace through your code. Make sure each expression has the type you expect it to have.
""".format(filename=TEST_FILENAME)).strip(), student.feedback.message)

    def test_error_context(self):
        student_code = dedent('''
                    def get_input():
                        return int(input("Gimme the number"))
                ''')
        set_source(student_code, "student.py")
        student = Sandbox()
        student.run()
        result = student.call("get_input", inputs="Banana")
        print("--", [c.inputs for c in student._context])
        self.assertEqual(3, student.feedback.location.line)
        self.assertEqual(dedent(
            """I ran the code:
    get_input()

And I entered as input:
    Banana 
    
A ValueError occurred:

    Invalid literal for int() with base 10: 'Banana'

The traceback was:
Line 3 of file student.py in get_input
        return int(input("Gimme the number"))
""" + ('               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n' if IS_AT_LEAST_PYTHON_311 else "") + """
A ValueError occurs when you pass the wrong type of value to a function. For example, you try to convert a string without numbers to an integer (like `int('Five')`).

Suggestion: Read the error message to see which function had the issue. Check what type the function expects. Then trace your code to make sure you pass in that type.""").strip(), student.feedback.message)

    def test_call(self):
        student_code = "def average(a,b):\n return (a+b)/2"
        student = Sandbox()
        student.run(student_code, filename='student.py')
        student.call('average', 10, 12)

    def test_commands_api(self):
        clear_report()
        student_code = 'word = input("Give me a word")\nprint(word+"!")'
        set_source(student_code)
        self.assertFalse(commands.get_output())
        commands.queue_input("Hello")
        self.assertIsInstance(commands.run(), Sandbox)
        self.assertEqual(["Give me a word", "Hello!"],
                         commands.get_output())
        commands.queue_input("World", "Again")
        self.assertIsInstance(commands.run(), Sandbox)
        self.assertEqual(commands.get_output(),
                         ["Give me a word", "Hello!",
                          "Give me a word", "World!"])
        self.assertIsInstance(commands.run(), Sandbox)
        self.assertEqual(commands.get_output(),
                         ["Give me a word", "Hello!",
                          "Give me a word", "World!",
                          "Give me a word", "Again!"])
        commands.reset_output()
        commands.queue_input("Dogs", "Are", "Great")
        self.assertIsInstance(commands.run(), Sandbox)
        self.assertIsInstance(commands.run(), Sandbox)
        self.assertIsInstance(commands.run(), Sandbox)
        self.assertEqual(commands.get_output(),
                         ["Give me a word", "Dogs!",
                          "Give me a word", "Are!",
                          "Give me a word", "Great!"])
        
        
        commands.reset_output()
        commands.queue_input(json.dumps("Virginia,Trend"))
        self.assertIsInstance(commands.run(), Sandbox)
        self.assertEqual(commands.get_output(),
                         ["Give me a word", '"Virginia,Trend"!'])

    def test_commands_exceptions(self):
        student_code = '1 + "Banana"'
        set_source(student_code)
        commands.run()
        self.assertIsNotNone(commands.get_exception())


    def test_good_unique_calls(self):
        student_code = dedent("""
        def x(n):
            if n > 0:
                return x(n-1)
            return 0
        x(5)
        x(4)
        """)
        set_source(student_code)
        commands.start_trace()
        commands.run()
        self.assertEqual(commands.count_unique_calls('x'), 6)

    def test_tracing_returns(self):
        student_code = dedent("""
        def x(n):
            if n > 0:
                return x(n-1)*2
            return 1
        x(5)
        x(4)""")
        set_source(student_code)
        commands.start_trace()
        student = commands.run()
        self.assertEqual(len(student.trace.calls), 1)
        self.assertEqual(len(student.trace.calls['x']), 11)
        self.assertEqual(len(student.trace.returns), 1)
        self.assertEqual(len(student.trace.returns['x']), 11)
        self.assertEqual(student.trace.calls['x'][0], {'n': 5})
        self.assertEqual(student.trace.returns['x'][0], [32])

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
        student.run(student_code, filename='student.py')
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
        contextualize_report(student_code)
        student = run(student_code, filename='student.py')
        self.assertIn('plotting', dir(student.modules))
        plt = student.modules.plotting
        self.assertEqual(len(plt.plots), 1)
        self.assertIsNone(student.exception)

    def test_matplotlib_commands(self):
        student_code = dedent('''
            import matplotlib.pyplot as plt
            plt.plot([1,2,3])
            plt.title("My line plot")
            plt.show()
            plt.hist([1,2,3])
            plt.show()
        ''')
        contextualize_report(student_code)
        student = commands.run()
        print(student)
        plt2 = student.modules.plotting
        self.assertEqual(len(plt2.plots), 2)

    def test_blocked_module_import(self):
        student_code = dedent('''
            import os
            os
        ''')
        set_source(student_code)
        exception = commands.run()
        self.assertIsNotNone(exception)

    def test_coverage(self):
        test_filename = here+'_sandbox_test_coverage.py'
        with open(test_filename) as student_file:
            student_code = student_file.read()
        contextualize_report(student_code)
        student = Sandbox()
        student.tracer_style = 'native'
        student.run(student_code, filename=test_filename)
        self.assertIsNone(student.exception)
        #self.assertEqual(round(student.trace.pc_covered), 85)

        if IS_AT_LEAST_PYTHON_310:
            self.assertEqual([1, 2, 3, 4, 5, 6, 9, 12, 16, 14, 15, 17], student.trace.lines)
        else:
            self.assertEqual([1, 2, 3, 4, 6, 9, 12, 16, 14, 15, 17], student.trace.lines)


    def test_coverage_native(self):
        test_filename = here+'_sandbox_test_coverage.py'
        with open(test_filename) as student_file:
            student_code = student_file.read()
        contextualize_report(student_code)
        student = Sandbox()
        student.tracer_style = 'native'
        student.run(student_code, filename=test_filename)
        self.assertIsNone(student.exception)
        if IS_AT_LEAST_PYTHON_310:
            self.assertEqual(student.trace.lines, [1, 2, 3, 4, 5, 6, 9, 12, 16, 14, 15, 17])
        else:
            self.assertEqual(student.trace.lines, [1, 2, 3, 4, 6, 9, 12, 16, 14, 15, 17])
        self.assertEqual(student.trace.calls, {'z': [{'args': (0,), 'banana': 2, 'kwargs': {'apple': 8}, 'p': 3}]})

    def test_calls(self):
        student_code = dedent('''
            def x(n):
                if n > 0:
                    return x(n-1)
                return 0
            x(5)
        ''')
        student = Sandbox()
        student.tracer_style = 'calls'
        student.run(student_code, filename='student.py')
        self.assertEqual(len(student.trace.calls['x']), 6)


    def test_runtime_error_inputs(self):
        student_code = dedent('''
                    def x():
                        value = input("Gimme a number")
                        return 7 % value
                    x
                ''')
        student = Sandbox()
        set_source(student_code)
        student.run()
        result = student.call("x", inputs=["0"])

        self.assertEqual(("""I ran the code:
    x()

And I entered as input:
    0 

A TypeError occurred:

    Unsupported operand type(s) for %: 'int' and 'str'

The traceback was:
Line 4 of file answer.py in x
        return 7 % value
""" + ('               ^^^^^^^^^\n' if IS_AT_LEAST_PYTHON_311 else "") +"""
Type errors occur when you use an operator or function on the wrong type of value. For example, using `+` to add to a list (instead of `.append`), or dividing a string by a number.

Suggestion: To fix a type error, you should trace through your code. Make sure each expression has the type you expect it to have.
""").strip(), student.feedback.message)

    def test_unittest(self):
        student_code = dedent('''
            x = 0
        ''')
        student = Sandbox()
        student.run(student_code)
        student.call('x')
        self.assertIsNotNone(student.exception)

        student_code = dedent('''
        class Fruit:
            def __init__(self, name, weight=0):
                self.name = name
                self.weight = weight
        def do_math(a, b):
            return a + b - 5
        def weigh_fruits(fruits):
            return sum(fruit.weight for fruit in fruits)    
        ''')
        student.report.contextualize(Submission(main_code=student_code))
        student = Sandbox()
        student.run()
        result = student.call('do_math', 15, 20)
        self.assertEqual(result, 30)
        self.assertEqual(['do_math(15, 20)'],
                         [context.code for context in student.get_context()])
        banana = student.call('Fruit', "Banana")
        self.assertIsInstance(banana, student.data['Fruit'])
        self.assertEqual(["Fruit('Banana')"],
                         [context.code for context in student.get_context()])
        student.start_grouping_context()
        student.run()
        orange = student.call("Fruit", "Orange", 30, target="orange")
        self.assertIsInstance(orange, student.data['Fruit'])
        student.call("Fruit", "Pineapple", 60, target="pineapple")
        student.run("fruits = [orange, pineapple]")
        total_weight = student.call('weigh_fruits', args_locals=["fruits"])
        self.assertEqual(total_weight, 90)
        self.assertEqual([student_code,
                          "orange = Fruit('Orange', 30)",
                          "pineapple = Fruit('Pineapple', 60)",
                          "fruits = [orange, pineapple]",
                          "weigh_fruits(fruits)"],
                         [context.code for context in student.get_context()])
        # print(student.call('weigh_fruits', student.var['fruits']))
        # from pprint import pprint
        # pprint(student.call_contexts)

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
    
    def test_sandboxing_open(self):
        student_code = dedent('''
            print(open("test_sandbox.py").read())
        ''')
        set_source(student_code)
        student = Sandbox()
        student.run(student_code, filename='student.py')
        self.assertEqual(str(student.exception), "The filename you passed to 'open' is restricted.")
        # Then can we turn it back on?
        student.allow_function('open')
        student.run(student_code, filename='student.py')
        self.assertIsNone(student.exception)
        # And off again
        student.block_function('open')
        student.run(student_code, filename='student.py')
        self.assertEqual(str(student.exception), "You are not allowed to call 'open'.")

    def test_block_requests_module(self):
        student_code = dedent('''
            import os
            print(os.listdir())
        ''')
        set_source(student_code)
        student = Sandbox()
        student.block_module('os')
        student.run(student_code, filename='student.py')
        self.assertEqual(str(student.exception), "You cannot import `os` from student code.")
        # Then can we turn it back on?
        student.allow_module('os')
        student.run(student_code, filename='student.py')
        self.assertIsNone(student.exception)
        # And off again
        student.reset_default_overrides()
        student.block_module('os')
        student.run(student_code, filename='student.py')
        self.assertEqual(str(student.exception), "You cannot import `os` from student code.")

    def test_sandboxing_pedal(self):
        student_code = dedent('''
            from pedal.report import MAIN_REPORT
            print(MAIN_REPORT)
        ''')
        set_source(student_code)
        student = Sandbox()
        student.run(student_code, filename='student.py')
        self.assertEqual(str(student.exception), "You cannot import pedal!")
    
    def test_sandboxing_sys_modules(self):
        clear_report()
        student_code = dedent('''
            import sys
            # Might try to bypass us
            del sys.modules['pedal']
            from pedal.report import MAIN_REPORT
            print(MAIN_REPORT)
        ''')
        set_source(student_code)
        student = Sandbox()
        student.run(student_code, filename='student.py')
        self.assertEqual(str(student.exception), "You cannot import pedal!")
    
    def test_sandboxing_devious_open1(self):
        student_code = dedent('''
            __builtins__['globals']()['open']("test_sandbox.py")
            # Fine to import anything else
            
        ''')
        set_source(student_code)
        student = Sandbox()
        student.run(student_code, filename='student.py')
        self.assertEqual(str(student.exception), "You are not allowed to call 'globals'.")

    def test_mock_turtle(self):
        student_code = dedent('''
            import turtle
            turtle.forward(100)
            turtle.mainloop()
        ''')
        set_source(student_code)
        student = Sandbox()
        student.run(student_code, filename='student.py')
        self.assertIsNone(student.exception)
        self.assertEqual(student.modules.turtles.calls[0][0], 'forward')
        self.assertEqual(student.modules.turtles.calls[0][1][0], 100)

    def test_weird_module_behavior(self):
        student_code = dedent('''
                    import pprint
                    pprint.pprint(5)
                ''')
        set_source(student_code)
        student = Sandbox()
        student.run(student_code, filename='student.py')
        self.assertIsNone(student.exception)

    def test_range_requires_integer(self):
        contextualize_report("x = 5")
        commands.run()
        x = commands.evaluate("x")
        range(x)
        self.assertIsNone(commands.get_exception())

    def test_int_requires_integer(self):
        contextualize_report("x = '5'")
        commands.run()
        x = int(commands.evaluate("x"))
        self.assertIsNone(commands.get_exception())

    def test_block_exit(self):
        contextualize_report("exit()")
        commands.run()
        self.assertIsNotNone(commands.get_exception())

    @unittest.skip("TODO: Something weird with recursion")
    def test_bad_recursion(self):
        contextualize_report("""
def to_pig_latin(str):
    first = str[0]
    str = str[1:]
    str = str + first + "ay"
    to_pig_latin("hello")""")
        commands.run()
        commands.call('to_pig_latin', 'test', threaded=True)
        self.assertNotIsInstance(commands.get_exception(), RecursionError)

    def test_duplicate_parameters(self):
        contextualize_report("def x(y,y): pass")
        commands.run()
        self.assertIsNotNone(commands.get_exception())

    def test_imported_input_is_mocked(self):
        contextualize_report(Submission({
            "answer.py": "from another import call_input\nprint(call_input())",
            "another.py": "def call_input():\n return input()"
        }))
        #commands.mock_module("another", {"call_input": lambda: input()}, "another")
        commands.queue_input("XYZ")
        commands.run()
        self.assertIsNone(commands.get_exception())
        self.assertEqual(["", "XYZ"], commands.get_output())

    # TODO: test `import builtins` strategy to access original builtins

    def test_sandbox_result_all_operators_int_float(self):
        operators = [
            ('*', '__mul__', lambda x, y: x * y),
            ('+', '__add__', lambda x, y: x + y),
            ('-', '__sub__', lambda x, y: x - y),
            ('/', '__truediv__', lambda x, y: x / y),
            ('//', '__floordiv__', lambda x, y: x // y),
            ('%', '__mod__', lambda x, y: x % y),
            ('**', '__pow__', lambda x, y: x ** y),
        ]
        types = [
            ('sandbox_int', SandboxResult(7), 7),
            ('float', 3.0, 3.0),
            ('int', 5, 5),
            ('sandbox_float', SandboxResult(2.0), 2.0),
        ]
        for operator, name, as_function in operators:
            for (type1, value1, e1), (type2, value2, e2) in itertools.product(types, types):
                with self.subTest(operator=operator, type1=type1, value1=value1, type2=type2, value2=value2):
                    student_code = f"x = {value1}\ny = {value2}"
                    set_source(student_code)
                    actual = as_function(value1, value2)
                    expected = as_function(e1, e2)
                    print(value1, operator, value2, "=", actual, expected)
                    self.assertEqual(actual, expected, msg=f"actual={actual}, expected={expected}, "
                                                           f"operator={operator}, name={name}, type1={type1}, "
                                                           f"value1={value1}, type2={type2}, value2={value2}")

    def test_sandbox_result_all_operators_str(self):
        test_cases = [
            # Multiplication
            ('*', lambda x, y: x * y, [
                ('int', 5, 5, 'str', "Hello", "Hello"),
                ('sandbox_int', SandboxResult(5), 5, 'str', "Hello", "Hello"),
                ('int', 5, 5, 'sandbox_str', SandboxResult("Hello"), "Hello"),
                ('sandbox_int', SandboxResult(5), 5, 'sandbox_str', SandboxResult("Hello"), "Hello"),
                ('str', "Hello", "Hello", 'int', 5, 5),
                ('sandbox_str', SandboxResult("Hello"), "Hello", 'int', 5, 5),
                ('str', "Hello", "Hello", 'sandbox_int', SandboxResult(5), 5),
                ('sandbox_str', SandboxResult("Hello"), "Hello", 'sandbox_int', SandboxResult(5), 5),
            ]),
            # Addition
            ('+', lambda x, y: x + y, [
                ('str', "Hello", "Hello", 'str', " World", " World"),
                ('sandbox_str', SandboxResult("Hello"), "Hello", 'str', " World", " World"),
                ('str', "Hello", "Hello", 'sandbox_str', SandboxResult(" World"), " World"),
                ('sandbox_str', SandboxResult("Hello"), "Hello", 'sandbox_str', SandboxResult(" World"),
                 " World"),
            ])
        ]
        for operator, as_function, test_cases in test_cases:
            for type1, value1, e1, type2, value2, e2 in test_cases:
                with self.subTest(operator=operator, type1=type1, value1=value1, type2=type2, value2=value2):
                    student_code = f"x = {value1}\ny = {value2}"
                    set_source(student_code)
                    actual = as_function(value1, value2)
                    expected = as_function(e1, e2)
                    print(value1, operator, value2, "=", actual, expected)
                    self.assertEqual(actual, expected, msg=f"actual={actual}, expected={expected}, "
                                                           f"operator={operator}, type1={type1}, value1={value1}, "
                                                           f"type2={type2}, value2={value2}")
if __name__ == '__main__':
    unittest.main(buffer=False)

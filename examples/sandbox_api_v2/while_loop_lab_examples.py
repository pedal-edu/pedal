from pedal import (set_source, next_section, execute)
from pedal.assertions import *

# Validate source code file
# set_source(code=None, filename=None, sections=None, independently=False)
#   code is not None: load from string
#   code is None and filename is String: load from explicit filename
#   code and filename are None: load from first sys.args parameter
# There are 6 sections here. Could have left it at None to have one big file.
# Process each section building on the previous
#   independently=True is useful for exam mode, where each section is its own
#   parse tree. Default is False, though
set_source(sections=6, independently=False)

# Start off in section 0
# Usually, that's just header (e.g., author names), so we want to advance to the
# next section.

# So now we'll go to Section 1
# This also immediately executes the new section.
#   Using the API, you could separate these two actions - but not sure you'd
#   ever need to. Priority levels handle the concept of "Checking syntax" before
#   runtime stuff. Ah, but you might want to mock some functions.
student = next_section()

''' Create a function `factorial` '''

@section(1)
def problem_1_factorial_defined():
    """

    """
    assertHasFunction(student, 'factorial')
    assertSignature(student.data.factorial, args=["int"], returns="int")

@precondition(problem_1_factorial_defined)
@try_all()
def problem_1_factorial_unit_tests():
    """

    """
    # Using student.call ensures that the call is safely sandboxed
    # The function call actually returns a SandboxResult object which has
    #   several useful functions
    #       .result is the actual result value
    #       .calls is the number of times the function was called this time
    # All four of these will run, but if any of them fail we stop processing overall.
    assertEqual(student.call('factorial', 4), 24, score=.25)
    assertEqual(student.call('factorial', 8), 40320, score=.25)
    assertEqual(student.call('factorial', 0), 1, score=.25)
    assertEqual(student.call('factorial', 1), 1, score=.25)
    # If you fail one, the message looks like:
    # I called
    # > factorial(4)
    # I expected
    # > 24
    # But I received
    # > XYZ
    
@precondition(problem_1_factorial_unit_tests)
def problem_1_factorial_recursive():
    """

    """
    # Ensure that they called it recursively
    if student.call('factorial', 5).calls <= 5:
        explain("factorial(5) did not execute 5 times recursively.")

@precondition(problem_1_factorial_defined)
def problem_1_factorial_does_not_start_at_zero():
    """

    """
    assertHasFunction(student, 'factorial')
    assertNotEqual(student.call('factorial', 0), 0,
                   message="factorial(0) is not 0.")
                   
@precondition(problem_1_factorial_defined)
def problem_1_prevent_illegal_iteration():
    """

    """
    factorial_definition = find_definition('factorial')
    if factorial_definition.is_method():
        explain("factorial should be a function, not a method.")
    # Other options: "recursion", "comprehension"
    prevent_iteration(factorial_definition, "while", "for", "higher-order")
    # Toolkit functions can have their automatic explanations turned off
    #   so you can use them in your own way.
    #   can also use toolkit.give_explanations(False)
    if prevent_iteration(factorial_definition, "comprehension", explain=False):
        explain("Woah, don't use a comprehension!")
        
@finish_section(1)
def problem_1_factorial_complete():
    """

    """
    compliment("You completed the factorial function")
    
# Alternatively, you can explicitly list all the functions for this section
# and manually resolve them
'''
resolve_section(problem_1_factorial_defined,
                problem_1_factorial_does_not_start_at_zero,
                problem_1_factorial_recursive,
                problem_1_factorial_unit_tests,
                problem_1_prevent_illegal_iteration,
                problem_1_factorial_complete)
'''

# Any unresolved decorated tests will be resolved before advancing
# to the next section.
# If we're working `independently`, then the next section will run regardless,
#   but otherwise it will stop the overall resolving here.
student = next_section()

''' Create a function sum_numbers that takes user input (e.g., '1+2+3')
    and prints the sum of the numbers given (6). If users type in something
    that is not valid (series of digits and +), repeatedly prompt them for
    new input.'''

@section(2)
def problem_2_sum_numbers_defined():
    """

    """
    assertHasFunction(student, 'sum_numbers')
    assertSignature(student.data.sum_numbers, args=[], 
                    returns=None, input=True, prints=True)

@precondition(problem_2_sum_numbers_defined)
@try_all()
def problem_2_sum_numbers_unit_tests():
    """

    """
    # input can take a string or a list of strings
    #   If the user has an argument named input, you can use _input for it.
    #   Otherwise, positional and keyword arguments are passed to the call.
    # assertPrints confirms that they printed AS A RESULT of calling the
    #   function, not just that it was in the output.
    #   It can use a string or a list of strings. It can match exactly or
    #   approximately.
    assertPrints(student.call.sum_numbers(input="1"), "1", score=.25)
    assertPrints(student.call.sum_numbers(input="1+2"), "3", score=.25)
    assertPrints(student.call.sum_numbers(input="2+3+4"), "9", score=.25)
    assertPrints(student.call.sum_numbers(input=""), "0", score=.25)
    
@precondition(problem_2_sum_numbers_defined)
@try_all()
def problem_2_sum_numbers_bad_input():
    """

    """
    assertPrints(student.call.sum_numbers(input=["A", "???", "1"]), "1", score=.25)
    assertPrints(student.call.sum_numbers(input=["1+A", "XY+YZ", "!", "1+2"]), "3", score=.25)
    
student = next_section()
    
''' Create a variable poem and put in a string value. Must have at least a
    letter, number, symbol, and a new line. '''

@section(3)
def problem_3_make_string_variable():
    """

    """
    assertHas(student, 'poem')
    assertIsInstance(student.data.poem, str)

import string
@precondition(problem_3_make_string_variable)
@try_all()
def problem_3_string_has_characters():
    """

    """
    assertRegex(student.data.poem, '[{}]'.format(string.digits),
                message="Your poem must have a digit in it.")
    assertRegex(student.data.poem, '[{}]'.format(string.punctuation),
                message="Your poem must have a symbol in it.")
    assertRegex(student.data.poem, '[{}]'.format(string.letters),
                message="Your poem must have a letter in it.")
    
    
student = next_section()

''' Create a class `Account` '''

@section(4)
def problem_4_defined_account():
    """

    """
    assertHasClass(student, 'Account')
    assertSignature(student.data.Account, args=['str'], attrs={'name': 'str'})

@precondition(problem_4_defined_account)
def problem_4_account_attrs():
    """

    """
    student.call('Account', 'My Checking', target="checking_account")
    assertHasAttr(student.data.checking_account, 'balance', (int, float))
    # Can do the comparison separately, if you need a special comparison
    assertEqual(student.data.checking_account.balance, 0)
    # Or default to equal check as third parameter
    assertHasAttr(student.data.checking_account, 'name', str, "My Checking")

student = next_section()
    
''' Add a method `deposit` '''
@section(5)
def problem_5_defined_deposit():
    """

    """
    assertHasFunction(student, 'Account.deposit')
    assertSignature(student.data.Account.deposit, args=['int'],
                    returns='int')

@precondition(problem_5_defined_deposit)
@contextualize_calls()
def problem_5_unit_tests():
    """

    """
    # By default, the context list gets reset each time we enter the function.
    student.call('Account', 'My Checking', target="checking_account")
    assertEqual(student.call('checking_account.deposit', 400), 400)
    assertEqual(student.call('checking_account.deposit', 100), 500)
    # If this failed, it would print out:
    # I called all of the following:
    # > checking_account = Account('My Checking')
    # > checking_account.deposit(400)
    # Then I called:
    # > checking_account.deposite(100)
    # I expected it to produce
    # > 500
    # Instead, it produced:
    # > XYZ
    # Could also use instead:
    #   student.data.checking_account
    checking_account = student.data.checking_account
    assertEqual(checking_account.balance, 500)
    
next_section(execute=False)
# Use the default matplotlib mock; could also throw in your own using our API.
# class MockMatplotlib(MockedModule):
#   _module_name = 'matplotlib.pyplot'
#   def plot(self, **kwargs):
#       pass
student = execute(modules={'matplotlib': True})

''' Make a histogram '''
    
@section(6)
def problem_6_make_graph():
    """

    """
    plt = student.modules['matplotlib.pyplot']
    # Check if they madea  graph of the wrong type?
    assertGraphCount(plt, 1)
    # plt.plots.by_type('histogram')
    # plt.plots.by_data(X)
    assertGraphType(plt.plots[0], 'histogram')
    with open('golden_file.yaml') as golden_file:
        golden_data = yaml.load(golden_file)
    assertGraphData(plt.plots[0], golden_data['X'])

# assertEqual(left, right, score=None, message=None, match_exactly=False)
# assertPrints(left, right, score=None, message=None, match_exactly=False)

# Resolves all remaining functions.
resolve_all()

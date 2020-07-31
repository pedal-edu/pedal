from pedal import separate_into_sections
from pedal.source.sections import *
from pedal.assertions.feedbacks import assert_group
from pedal.core.commands import *
from pedal.sandbox.commands import run, start_trace, stop_trace, get_trace
from pedal.assertions.runtime import *

contextualize_report("a = 0")

start_trace()
student = run()
stop_trace()

assert_coverage(.5,
                message="You will only be given feedback if you have at least 50% code coverage. Write some more unit tests!",
                category='instructor',
                priority='high')

separate_into_sections()


@section(1, score=1/3)
def q1_1():
    assertHasFunction(student, 'add_5', args=["num"]*5, returns="str")
    with assert_group('add'):
        assertEqual(student.call('add_5', 1,2,3,4,5), "12345")
        assertEqual(student.call('add_5', 5,4,3,2,1), "54321")
        assertEqual(student.call('add_5', 0,0,0,0,0), "00000")
    set_success(message="#1.1) You completed the add_5 function",
                group=section(1))


with section(1, score=1/3) as section1:
    set_success(message="#1.1) You completed the first section.",
                group=section1)

@section(1)
# Does not require them to complete q1_1 because it's not a precondition
def q1_2():
    """

    """
    assertHasFunction(student, 'third', args=["list[any]"], returns="any")
    with try_all():
        assertEqual(student.call("third", [1, 3, 5]), 5, score=.25)
        assertEqual(student.call("third", ["Alpha", "Beta", "Gamma", "Delta"]), 
                    "Gamma", score=.25)
        assertEqual(student.call("third", [1, 2]), None, score=.125)
        assertEqual(student.call("third", []), None, score=.125)
    compliment("#1.2) You completed the third function", score=.25)

@section(1)
def q1_3():
    """

    """
    assertHasFunction(student, 'is_question', args=["str"], returns="bool")
    with try_all():
        assertEqual(student.call("is_question", "Huh?"), True, score=.25)
        assertEqual(student.call("is_question", "A longer string?"), True, score=.25)
        assertEqual(student.call("is_question", "OH NO!"), False, score=.25)
        assertEqual(student.call("is_question", "??????!"), False, score=.25)
        assertEqual(student.call("is_question", ""), False, score=.25)
    compliment("#1.3) You completed the is_question function", score=.25)

student = next_section()
    

class Lab12(SectionalAssignment):
    filename = 'lab12.py'
    max_points = MP
    sections = 5
    
    def test_part_1(self):
        """

        Returns:

        """
        reset()
        student = run(threaded=True)
        
        all_done = 0
                               
        # Question 1.1
        if match_signature('add_5', 5):
            if student.tests('add_5',
                             [['12345', 1,2,3,4,5],
                              ['54321', 5,4,3,2,1],
                              ['00000', 0,0,0,0,0]],
                             5,
                             "#1.1) You completed the add_5 function."):
                all_done += 1
        
        # Question 1.2
        if match_signature('third', 1):
            if student.tests('third',
                             [[5, [1, 3, 5]],
                              ["Gamma", ["Alpha", "Beta", "Gamma", "Delta"]],
                              [None, [1, 2]],
                              [None, [1]],
                              [None, []]],
                             5,
                             "#1.2) You completed the third function."):
                all_done += 1
        
        # Question 1.3
        if match_signature('is_question', 1):
            if student.tests('is_question',
                             [[True, "Huh?"],
                              [True, "A longer string?"],
                              [False,"OH NO!"],
                              [False,"????????!"],
                              [False, ""]],
                             5,
                             "#1.3) You completed the is_question function."):
                all_done += 1
        
        if all_documented():
            all_done += 1
        
        return all_done >= 4
    
    def test_part_2(self):
        """

        Returns:

        """
        reset()
        student = run()
        
        all_done = 0
        
        # Question 2.1
        if check_function('summate', 1):
            if student.tests('summate',
                             [[12, [5, 3, 4]],
                              [100, [50, 10, 20, 20]],
                              [0, []]],
                             5,
                             "#2.1) You completed the summate function."):
                all_done += 1
        
        # Question 2.2
        if check_function('join_digits', 1):
            if student.tests('join_digits',
                              [ ["12345", [1, 2, 3, 4, 5]],
                                ["654321", [6, 5, 4, 3, 2, 1]],
                                ["", []]
                              ],
                              5,
                              "#2.2) You completed the join_digits function."):
                all_done += 1
        
        # Question 2.3
        if check_function('is_numeric', 1):
            if student.tests('is_numeric',
                              [ [True, "12345"],
                                [True, "654321"],
                                [False, ""],
                                [False, "12B"],
                                [False, "AB5"]
                              ],
                              5,
                              "#2.3) You completed the is_numeric function."):
                all_done += 1
        
        # Question 2.4 and 2.5
        if check_method(student.data, 'Food', "__init__", 4):
            student.call('Food', "Grapes", 12, 4, _target="grapes")
            student.raise_any_exceptions()
            context = "I created a Food:\n<pre>> grapes = Food('Grapes', 12, 4)</pre>\n"
            if not check_attribute(student.data, 'grapes', "name", str, "Grapes", context):
                return False
            elif not check_attribute(student.data, 'grapes', "quantity", (int, float), 12, context):
                return False
            elif not check_attribute(student.data, 'grapes', "price", (int, float), 4, context):
                return False
            elif 'my_grocery_list' not in student.data:
                explain("You need to make that my_grocery_list variable!")
                return False
            else:
                my_grocery_list = student.data['my_grocery_list']
                Food = student.data['Food']
                Food.__repr__ = lambda s: "Food('{}', {}, {})".format(s.name, s.quantity, s.price)
                # Question 2.4
                if not isinstance(my_grocery_list, list):
                    explain("The my_grocery_list variable is not a list.")
                    return False
                elif len(my_grocery_list) != 3:
                    explain("The my_grocery_list list should have 3 elements in it.")
                    return False
                elif not all(isinstance(item, Food) for item in my_grocery_list):
                    explain("At least one of your grocery items was not Food.")
                    return False
                else:
                    # Question 2.4
                    if check_function('total_cost', 1):
                        if student.tests('total_cost',
                                         [ [60, my_grocery_list],
                                           [100, [Food("Flower", 10, 10)]],
                                           [0, []]
                                         ],
                                         5,
                                         "#2.4) You completed the total_cost function."):
                            all_done += 1
        
        if all_documented():
            all_done += 1
        
        return all_done >= 5
    
    def test_part_3(self):
        """

        Returns:

        """
        reset()
        student = run()
        
        all_done = 0
        
        if check_function('sum_grades', 1):
            if student.tests('sum_grades',
                              [ [27, [[1, 2, 3], [4, 5, 6], [1, 2, 3]]],
                                [0, []],
                                [10, [[1,1], [4,4]]]
                              ],
                              5,
                              "#3.1) You completed the sum_grades function."):
                all_done += 1
        
        if check_function('average_grades', 1):
            if student.tests('average_grades',
                              [ [3., [[1, 2, 3], [4, 5, 6], [1, 2, 3]]],
                                [None, []],
                                [2.0, [[1, 1], [4]]],
                                [2.5, [[1,1], [4,4]]]
                              ],
                              5,
                              "#3.2) You completed the average_grades function."):
                all_done += 1
        
        Food = student.data['Food']
        Food.__repr__ = lambda s: "Food('{}', {}, {})".format(s.name, s.quantity, s.price)
        grocery_lists1 = [[Food("Gallon of Shrimp", 3, 10)]]
        grocery_lists2 = [ [Food("Ham", 1, 6), Food("Milk", 2, 2)],
                           [Food("Pickled hamburgers", 4, 1), Food("Ketchup", 40, 2), Food("BBQ Peeps", 10, 1)],
                           [Food("A Grape", 3, 1)]]
        grocery_lists3 = [ [Food("Melted Butter", 22, 1), Food("Cold dogs", 5, 2), Food("A dog", 1, 50)],
                           [Food("Toothpaste Jar", 5, 3)],
                           [Food("More Ketchup", 100, 2)]]
        if check_function('sum_grocery_lists', 1):
            if student.tests('sum_grocery_lists',
                             [ [30, grocery_lists1],
                               [107, grocery_lists2],
                               [297, grocery_lists3],
                               [0, []]
                             ],
                             5,
                             "#3.3) You completed the sum_grocery_lists function."):
                all_done += 1
        
        if all_documented():
            all_done += 1
        
        return all_done >= 4
    
    def test_part_4(self):
        """

        Returns:

        """
        reset()
        student = run()
        
        all_done = 0
        
        input_number_signature = match_signature('input_number', 0)
        if input_number_signature:
            if 'input_number' not in student.data:
                explain("Could not find the input_number function.")
            elif not callable(student.data['input_number']):
                explain("The input_number function was not callable.")
            else:
                input_number = student.data['input_number']
                def call_test(inputs):
                    """

                    Args:
                        inputs:

                    Returns:

                    """
                    student.call('input_number', _inputs=inputs, _threaded=True, _raise_exceptions=True)
                    if student.exception:
                        return False
                    if student._ != inputs[-1]:
                        explain(("I called<pre>input_number()</pre>\n"
                                "I entered<pre>{}</pre>\n"
                                "I expected it to produce<pre>{}</pre>\n"
                                "But it produced<pre>{}</pre>").format(
                                    "\n".join(inputs),
                                    repr(inputs[-1]),
                                    repr(student._)
                                ))
                        return False
                    return True
                worked_1 = call_test(["5"])
                worked_2 = call_test(["A", "5"])
                worked_3 = call_test(["A", "BBBBBB", "CCCC", "1F", "G3", "503"])
                if worked_1 and worked_2 and worked_3:
                    give_partial(5, "#4.1) You completed the input_number function.")
                    all_done += 1
                else:
                    return False
                    
        letter_per_line_signature = match_signature('letter_per_line', 0)
        if letter_per_line_signature:
            if 'letter_per_line' not in student.data:
                explain("Could not find the letter_per_line function.")
            elif not callable(student.data['letter_per_line']):
                explain("The letter_per_line function was not callable.")
            else:
                letter_per_line = student.data['letter_per_line']
                def call_test(input, output):
                    """

                    Args:
                        input:
                        output:

                    Returns:

                    """
                    student.set_output(None)
                    student.call('letter_per_line', _inputs=[input], _threaded=True, _raise_exceptions=True)
                    if student.exception:
                        return False
                    if not all(line in student.output for line in output):
                        explain(("I called<pre>letter_per_line()</pre>\n"
                                "I entered<pre>{}</pre>\n"
                                "I expected it to print<pre>{}</pre>\n"
                                "But it printed<pre>{}</pre>").format(
                                    input,
                                    "\n".join(output),
                                    "\n".join(student.output)
                                ))
                        return False
                    return True
                worked_1 = call_test("Ada", ["A", "d", "a"])
                worked_2 = call_test("Pumpkin", ["P", "u", "m", "p", "k", "i", "n"])
                if worked_1 and worked_2:
                    give_partial(5, "#4.2) You completed the letter_per_line function.")
                    all_done += 1
                else:
                    return False
        
        # Question 2.1
        summate_while_signature = match_signature('summate_while', 1)
        if summate_while_signature:
            if 'summate_while' not in student.data:
                explain("Could not find the summate_while function.")
            elif not callable(student.data['summate_while']):
                explain("The summate_while function was not callable.")
            else:
                def call_test(given, expected):
                    """

                    Args:
                        given:
                        expected:

                    Returns:

                    """
                    student.set_output(None)
                    student.call('summate_while', given, _threaded=True, _raise_exceptions=True)
                    if student.exception:
                        return False
                    if student._ != expected:
                        explain(("I called<pre>letter_per_line({})</pre>\n"
                                "I expected it to produce<pre>{}</pre>\n"
                                "But it produced<pre>{}</pre>").format(
                                    repr(given),
                                    repr(expected),
                                    repr(student._)
                                ))
                        return False
                    return True
                worked_1 = call_test([5, 3, 4], 12)
                worked_2 = call_test([50, 10, 20, 20], 100)
                worked_3 = call_test([], 0)
                if worked_1 and worked_2:
                    give_partial(5, "#4.3) You completed the summate_while function.")
                    all_done += 1
                else:
                    return False
        
        if all_documented():
            all_done += 1
        
        return all_done >= 4

Lab12().resolve()
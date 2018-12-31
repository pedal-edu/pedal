'''
exercise_id: 203
title: #30.1) Calorie List
topics:  Lists
prerequisites:
instructions:-----
Create a list of 3 numbers that represent the <a href="http://www.calorieking.com/foods/" target="_blank">calories of your favorite foods</a> and store these numbers in a variable. Print this variable.
-----
[systems]
language: Python
version: >= 3.3
on_run:-----
'''
from pedal import *

student = execute()

ast = parse_program()
declarations = len(ast.find_all("List")) + function_is_called("list")
assertGreater(declarations, 0, message="You must create a list.")
assertLess(declarations, 2, message="You should only have one list.")

variables = student.data.get_by_type(list)
assertGreater(len(variables), 0, message="You must create a new list variable.")
assertLess(len(variables), 2, message="Only create one list variable.")

calories = variables[0]
assertGreaterEqual(len(calories), 3, message="You need at least 3 numbers in your list variable.")

for element in calories:
    assertIsInstance(element, (int, float), message="All of the elements in the list must be numbers.")

assertPrints(student, repr(calories))

set_success()

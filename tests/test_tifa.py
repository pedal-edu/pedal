import traceback
import unittest
import os
import sys
from textwrap import dedent
from pprint import pprint
from dataclasses import dataclass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pedal.tifa
import pedal.types.new_types as defs
import pedal.types.normalize as normalize
from pedal import contextualize_report, Submission, evaluate
from pedal.tifa import tifa_provide_module_type

unit_tests = {

    # Function decorator
    'function_decorator':
        ['def dec(f):\n    return f\n@dec\ndef x(a: int):\n    return a\nx()', ['unused_variable'], []],

    # Source Code, Shouldn't catch this, Should catch this
    'builtin_True': ['print(True)', ['initialization_problem'], []],
    'unread_variable': ['a = 0', [], ['unused_variable']],
    'undefined_variable': ['print(a)', [], ['initialization_problem']],
    'defined_read_variable': ['a = 0\nprint(a)', ['initialization_problem'], []],
    'overwritten_variable': ['a = 0\na = 5', [], ['overwritten_variable']],
    'unread_variables': ['a = 0\nb = 5', ['overwritten_variable'], ['unused_variable']],
    'wrwr_variable': ['a = [1]\nprint(a)\na = [1]\nprint(a)', [], []],
    # unconnected_blocks
    'unconnected_assign': ['a = ___', [], ['unconnected_blocks']],
    'unconnected_print': ['print(___)', [], ['unconnected_blocks']],

    'literal_in_call': ['print("dog" in input("test"))', [], []],
    'wrong_method_for_type': ['[].replace(",","")', [], []],

    "check_true_argument_in_function_call":
        ['def is_true(x:bool)->bool:\n return x\nis_true(True)', 'parameter_type_mismatch', ''],

    # Double call
    'double_call': ['def x(a):\n    return a\nx(5)\nx(3)', ['read_out_of_scope'], []],

    # Chained functions
    'chained_functions': ['def x():\n    return 0\ndef y():\n    x()\ny()',
                          ['read_out_of_scope', 'initialization_problem'], []],

    # String indexing and slicing
    'string_indexing_slicing': ['("a"[0] + ""[:])[:][0]', ['incompatible_types'], []],
    # List indexing and slicing
    'list_indexing_slicing': ['([0][0] + [1,2,3][:][2])', ['incompatible_types'], []],

    'returned_string':
        [
            'def pluralize(a_word):\n    return a_word+"s"\nnoun = pluralize("Dog")\nprint(noun + " can pet other " + noun)',
            ['incompatible_types'], []],
    'update_without_read':
        ['a = 0\na+= 1', ['initialization_problem'], ['unused_variable']],
    'update_and_read':
        ['a = 0\na+= 1\nprint(a)', ['initialization_problem', 'unused_variable'], []],
    'iterate_through_non_existing_list':
        ['for x in y:\n\tpass', ['unused_variable'], ['initialization_problem']],
    'iterate_through_list':
        ['y = [1,2,3]\nfor x in y:\n\tpass', ['unused_variable', 'initialization_problem'], []],
    'iterate_through_empty_list':
        ['y = []\nfor x in y:\n\tpass', ['unused_variable', 'initialization_problem'], ['iterating_over_empty_list']],
    'double_iterate_through_strings':
        ['ss = ["Testing", "Here"]\nfor a in ss:\n    print(a)\nfor b in a:\n    print(b)',
         ['iterating_over_non_list', 'iterating_over_empty_list'], []],
    'iterate_through_number':
        ['y = 5\nfor x in y:\n\tpass', ['unused_variable', 'initialization_problem'], ['iterating_over_non_list']],
    'iterate_over_iteration_variable':
        ['y = [1,2,3]\nfor y in y:\n\tpass', [], ['iteration_problem']],
    'type_change':
        ['a = 0\nprint(a)\na="T"\nprint(a)', [], ['type_changes']],
    'defined_in_if_root_but_not_other':
        ['if True:\n\ta = 0\nprint(a)', [], ['possible_initialization_problem']],
    'defined_in_both_branches':
        ['if True:\n\ta = 0\nelse:\n\ta = 1\nprint(a)', ['possible_initialization_problem'], []],
    'defined_in_else_root_but_not_other':
        ['if True:\n\tpass\nelse:\n\ta = 1\nprint(a)', [], ['possible_initialization_problem']],
    'defined_in_if_branch_but_others':
        ['if True:\n\tif False:\n\t\ta = 0\nprint(a)', [], ['possible_initialization_problem']],
    'defined_before_if_branch_but_not_others':
        ['if True:\n\ta = 0\nif False:\t\tpass\nprint(a)', [], ['possible_initialization_problem']],
    'defined_after_if_branch_but_not_others':
        ['if True:\n\tif False:\n\t\tpass\n\ta = 0\nprint(a)', [], ['possible_initialization_problem']],
    'defined_within_both_if_branches_but_not_others':
        ['if True:\n\tif False:\n\t\ta=0\n\telse:\n\t\ta = 0\nprint(a)', [], ['possible_initialization_problem']],
    'defined_in_all_branches':
        ['if True:\n\tif False:\n\t\ta=0\n\telse:\n\t\ta = 0\nelse:\n\ta=3\nprint(a)',
         ['possible_initialization_problem'], []],
    'read_in_if_branch_but_unset':
        ['if True:\n\tprint(a)', [], ['initialization_problem']],
    'read_in_else_branch_but_unset':
        ['if True:\n\tpass\nelse:\n\tprint(a)', [], ['initialization_problem']],
    'read_in_both_branches_but_unset':
        ['if True:\n\tprint(a)\nelse:\n\tprint(a)', [], ['initialization_problem']],
    'overwritten_in_both_branches':
        ['a = 0\nif True:\n\ta = 0\nelse:\n\ta = 1', [], ['overwritten_variable']],
    'overwritten_in_one_branch':
        ['a = 0\nif True:\n\tpass\nelse:\n\ta = 1', ['overwritten_variable'], []],
    'overwritten_in_inner_branch':
        ['a = 0\nif True:\n\tif False:\n\t\ta = 0\nelse:\n\ta = 1', ['overwritten_variable'], []],
    'overwritten_in_all_branch':
        ['a = 0\nif True:\n\tif False:\n\t\ta = 0\n\telse:\n\t\ta = 2\nelse:\n\ta = 1', [], ['overwritten_variable']],
    'overwritten_in_all_branches2':
        ['a = 0\nif True:\n\tprint(a)\n\tif False:\n\t\ta = 0\n\telse:\n\t\ta = 2\nelse:\n\ta = 1',
         ['overwritten_variable'], []],

    # TODO: This test case still fails! Investigate why, it's something quite complex.
    'take_pattern':
        ['def take(l):\n'
         ' t=True\n'
         ' r=[]\n'
         ' for i in l:\n'
         '  if i==".":\n'
         '    t=False\n'
         '  elif t:\n'
         '    r.append(i)\n'
         ' return r\n'
         'take([1,2,3, ".", 5, 6])', ['unused_variable', 'possible_initialization_problem', 'initialization_problem'], []],

    # TODO: This test case still fails! Investigate why, it's something quite complex.
    'possibly_overwritten_in_elif_branch':
        ['highest = 0\nfor score in [1,2]:\n    if False:\n        pass\n    elif False:\n        pass\n    else:\n        highest = 0\nhighest',
         ['possible_initialization_problem'], []],

    'andy_overwritten_in_elif_branch':
    ['from rates import bill_small,bill_medium,bill_large\n# do not delete the above line\nfrom cisc106 import assert_equal\n\ndef total_bill(data,base):\n    ''\n    if data < 100:\n        bill= bill_small(data,base)\n        return bill\n    elif data <= 1000 and data>100:\n        return bill_medium(data,base)\n    elif data > 1000:\n        bill = bill_large(data,base)\n        return float(bill)\n\nassert_equal(total_bill(30,80.),80.)\nassert_equal(total_bill(150,80.),95.5)\nassert_equal(total_bill(3000,80.0),160.)',
     ['possible_initialization_problem'], []],

    # Iterating over the result of a builtin
    'print_range':
        ['x = range(100)\nprint(x)', ['iterating_over_non_list'], []],
    'iterate_range':
        ['x = range(100)\nfor y in x:\n    print(y)', ['iterating_over_non_list'], []],
    'iterate_over_ranges_atomic_subtype':
        ['x = range(100)\nfor y in x:\n    pass\nfor z in y:\n    print(z)', [], ['iterating_over_non_list']],
    'iterate_over_split':
        ['for x in "a,b,c".split(","):\n  x+""', ['iterating_over_non_list', 'iterating_over_empty_list'], []],
    'iterate_over_string_upper':
        ['for l in "abc".upper():\n  l+""', ['iterating_over_non_list', 'iterating_over_empty_list'], []],

    # incompatible_types
    'add_int_str':
        ['a = 5 + "ERROR"', [], ['incompatible_types']],
    'multiply_str_int':
        ['a = "ERROR" * 5', ['incompatible_types'], []],
    'unary_and_sub_int_int':
        ['-(5)+0', ['incompatible_types'], []],
    'simple_unary_op':
        ['+1', ['incompatible_types'], []],
    'unary_compare':
        ['-1 < 5', ['incompatible_types'], []],
    'iadd_int_int':
        ['a=0\na+=5\na', ['incompatible_types', 'unused_variable', 'initialization_problem', 'overwritten_variable'],
         []],
    'iadd_str_int':
        ['a=""\na+=5\na', ['unused_variable', 'initialization_problem', 'overwritten_variable'],
         ['incompatible_types']],
    'iadd_undefined':
        ['a+=5\na', ['unused_variable', 'overwritten_variable'], ['initialization_problem']],
    'iadd_unread':
        ['a=0\na+=5', ['initialization_problem', 'overwritten_variable'], ['unused_variable']],
    'string_in_string':
        ['"" in ""', ['incompatible_types'], []],
    "string_in_tuple_str":
        ['"" in ("", "")', ['incompatible_types'], []],
    "string_in_int":
            ['"" in 5', [], ['incompatible_types']],
    "string_in_tuple_int":
        ['"" in (5, 4)', [], ['incompatible_types']],
    "string_var_in_tuple_strings":
        ['food = "fruitless"\nfood in ("apple", "banana")', ['incompatible_types'], []],
    "iter_string_var_in_tuple_string":
        ['x = [""]\nfor y in x:\n y in ("", "")', ['incompatible_types'], [] ],
    "iter_int_var_in_tuple_int":
        ['x = [5]\nfor y in x:\n y in (3,)', ['incompatible_types'], [] ],
    "iter_int_var_in_tuple_string":
        ['x = [4]\nfor y in x:\n y in ("", "")', [], ['incompatible_types'] ],

    # Lambda
    'lambda_add':
        ['a = lambda: 0\nb=a()\nb+5', ['incompatible_types'], []],

    # Handle function definitions
    'uncalled_function':
        ['def named(x):\n\tprint(x)\n', ['initialization_problem'], ['unused_variable']],
    'called_int_function':
        ['def int_func(x):\n\treturn 5\nint_func(10)', [], []],
    'called_constant_function':
        ['def x():\n    return 4\nx()', ['unused_variable'], []],
    'overwritten_parameter':
        ['def x(v):\n  v = 0\n  return v\nx()', [], ['overwritten_variable']],
    'overwritten_variable_in_function':
        ['def x():\n  v = 0\n  v = 7\n  return v\nx()', [], ['overwritten_variable']],
    # Actions after returning
    'return_after_return':
        ['def x():\n    return 5\n    return 4\nx()', [], ['action_after_return']],
    'action_after_return_on_both_branches':
        ['def x():\n  if True:\n    return 4\n  else:\n    return 3\n  a = 0\n  print(a)\nx()', [],
         ['action_after_return']],
    # Function with subtypes
    'function_with_subtypes_add_int_list_int':
        ['def add_first(a_list):\n    for element in a_list:\n        return element + 5\nprint(add_first([1]))',
         ['incompatible_types'], []],
    'function_with_subtypes_add_int_list_str':
        ['def add_first(a_list):\n    for element in a_list:\n        return element + 5\nprint(add_first(["1"]))', [],
         ['incompatible_types']],
    'function_with_subtypes_add_int_primitive_int':
        ['def add_first(a_list):\n    for element in a_list:\n        return element + 5\nprint(add_first(1))', [],
         ['iterating_over_non_list']],
    'function_with_subtypes_add_int_primitive_str':
        ['def add_first(a_list):\n    for element in a_list:\n        return element + 5\nprint(add_first("1"))', [],
         ['incompatible_types']],
    # Out of scope
    'read_out_of_scope':
        ['def x(parameter):\n    return parameter\nx(0)\nparameter', [], ['read_out_of_scope']],
    'read_inside_of_scope':
        ['def x(parameter):\n    return parameter\nx(0)', ['read_out_of_scope'], []],
    'read_not_out_of_scope':
        ['def x():\n    if 1:\n        y=0\n    else:\n        y=1\n    y\nx()\nx()', ['read_out_of_scope'], []],

    # Function with annotations
    'annotated_parameters_correct':
        ['def x(n: int):\n    1+n\nx(5)', ['parameter_type_mismatch', 'incompatible_types'], []],
    'annotated_parameters_wrong_argument':
        ['def x(n: int):\n    1+n\nx("5")', [], ['parameter_type_mismatch']],
    'annotated_parameters_wrong_parameter':
        ['def x(n: int):\n    "1"+n\nx(5)', [], ['incompatible_types']],
    'annotated_parameters_append_list':
        ['def x(l: list):\n    l.append(1)\nx([])', ['parameter_type_mismatch', 'incompatible_types'], []],
    'annotated_returns_int':
        ['def x()->int:\n    return "Wrong"\nx()', [], ['multiple_return_types']],
    'annotated_returns_list_int':
        ['def x()->[int]:\n    return [1,2,3]\nx().append(4)', ['multiple_return_types', 'incompatible_types'], []],

    'append_to_empty_list':
        ['a = []\na.append(1)\nprint(a)', ['initialization_problem', 'unused_variable'], []],
    'append_to_non_empty_list':
        ['a = [1]\na.append(1)\nprint(a)', ['initialization_problem', 'unused_variable'], []],
    'append_to_undefined':
        ['a.append(1)\nprint(a)', ['unused_variable'], ['initialization_problem']],
    'append_to_unread':
        ['a=[]\na.append(1)', ['initialization_problem'], ['unused_variable']],
    'append_to_number':
        ['a=1\na.append(1)\nprint(a)', [], ['append_to_non_list']],

    'append_and_index':
        ['x=[]\nx.append(1)\nx[0]+1', ['incompatible_types'], []],
    'indexing_used':
        ['mag1 = 0\nmercalli = [0]\nmag1 = mercalli[mag1]\nmag1',
         ['initialization_problem', 'unused_variable', 'overwritten_variable'], []],

    'created_list_but_unread':
        ['old = [1,2,3]\nnew=[]\nfor x in old:\n\tnew.append(x)', [], ['unused_variable']],
    'created_list_but_undefined':
        ['old = [1,2,3]\nfor x in old:\n\tnew.append(x)\nprint(new)', [], ['initialization_problem']],

    'builtin_float_converter':
        ['a = float(5)\nb = "test"\nprint(a+b)', [], ['incompatible_types']],

    # Double iteration
    'iterate_over_list_of_tuples':
        ['for x,y in [(1,2), (3,4)]:\n    x, y', ['initialization_problem'], []],
    'iterate_over_items':
        ['record = {"A": 5, "B": 6}\nfor x,y in record.items():\n    x, y', ['initialization_problem'], []],
    'iterate_over_items_add':
        ['record = {"A": 5, "B": 6}\nfor x,y in record.items():\n    x+"", y+0',
         ['initialization_problem', "incompatible_types"], []],

    # Tuple, Multiple Assignment
    'multiple_assignment': ['a,b = 1,2\n1+a\nb', ['incompatible_types'], []],
    'tuple_index': ['tuple_box = (6, 8, 4)\nprint(tuple_box[0])', [], []],

    # Sets
    'set_creation': ['a = set([1,2,3])\nprint(a)', ['initialization_problem'], []],
    'set_addition': ['a = {"dog"}\na+"cat"', [], ['incompatible_types']],
    'set_union_good': ['a = {"dog"}\na|{"cat"}', ['incompatible_types'], []],
    'set_union_bad': ['a = {"dog"}\na|"cat"', [], ['incompatible_types']],

    # Dictionaries
    'set_key_in_dict': ['a = {}\na[1] = 0', [], []],
    'use_key_in_dict': ['a = {"x": 5, "y": "T"}\na["x"]+5', ['incompatible_types'], []],
    'use_key_in_lod': ['x=[{"a": 0, "b": True}, {"a": 1, "b": False}]\ny=x[0]\nz=y["a"]+0', ['incompatible_types'], []],
    'use_chained_key_in_lod': ['x=[{"a": 0, "b": True}, {"a": 1, "b": False}]\nnot x[1]["b"]', ['incompatible_types'],
                               []],
    'iterate_over_lod': ['ls=[{"a": 0, "b": True}, {"a": 1, "b": False}]\nfor x in ls:\n    x["a"]+0',
                         ['incompatible_types'], []],
    # TODO: Add stronger assertion this one, it shouldn't be a good one
    'incorrect_dict_iteration': ['dict = {"T": "V"}\nfor key,value in dict:\n    print(key)', [], []],
    'incorrect_dict_iteration2': ['dict = {"T": 0}\nfor i in dict:\n print(i, dict[i])', [], []],

    # Record type
    'record_type_simple': [
        ('Dog = {"Name": str, "Age": int, "Fluffy": bool}\n'
         'def do_stuff(a_dog: Dog) -> Dog:\n'
         '    a_dog["Name"]+""\n'
         '    a_dog["Age"] = a_dog["Age"]+5\n'
         '    return a_dog\n'
         'ada = {"Name": "Ada", "Age": 2, "Fluffy": True}\n'
         'do_stuff(ada)["Name"] + ""'
         ), ['incompatible_types'], []
    ],
    'dict_with_setter': [
        ('person1={"Name": "Babbage", "Age": 3}\n'
            'def make_older(a_dog: dict) -> int:\n'
            '    a_dog["Age"]+=1\n'
            '    return a_dog["Age"]\n'
            'make_older(person1) + 0'), ['incompatible_types', 'type_changes'], []
    ],
    'function_returns_typed_dict': [
        ('def count_words(words: str) -> {str: int}:\n'
         '  counts = {}\n'
         '  for word in words.split(","):\n'
         '    if word not in counts:\n'
         '      counts[word] = 0\n'
         '    counts[word] += 1\n'
         '  return counts\n'
         'count_words("alpha,alpha,beta,alpha")'), ['multiple_return_types'], []
    ],
    'record_type_in_list': [
        ('Test = {"a": str}\n'
         'def x(y: [Test]):\n'
         '  return y[0]["a"]\n'
         'x([{"a": "apple"}])'),
         ['Parameter Type Mismatch'], []
    ],

    # While
    'while_until_input': [
        'user = input("Give a word.")\nwhile user:\n    print(user)\n    user = input("Give another word.")',
        ['unused_variable'], []],

    # With
    'with_open':
        ['with open("A") as a:\n    print(a)', ['initialization_problem'], []],

    # List comprehensions
    'list_comprehension':
        ['a = [5 for x in range(100)]\nfor i in a:\n    5+i', ['iterating_over_non_list', 'incompatible_types'], []],

    # return_outside_function
    'no_return_outside_function':
        ['def x():\n    return 5\nx()', ['return_outside_function'], []],
    'return_outside_function':
        ['def x():\n    pass\nreturn 5\nx()', [], ['return_outside_function']],

    # Classes
    'class_definition':
        [
            'class A:\n    y = 0\n    def __init__(self, x):\n        self.x = 0\n        self.test()\n    def test(self):\n        self.x = 5\nA()',
            [], []],
    'instance_assignment':
        ['class A:\n pass\na = A()\na.b = 0\nb', [], ['initialization_problem']],
    'instance_assignment_alt':
        ['class A:\n pass\na = A()\na.b = 0\na.b', ['initialization_problem'], []],
    'constructor_assignment':
        ['class A:\n def __init__(self):\n  self.x=0\na=A()\na.x+""', [], ['incompatible_types']],
    'parameterized_constructor_assignment':
        [dedent("""
                class A:
                    def __init__(self, f):
                        self.y = f
                a = A(7)
                a.y + ''"""), [], ['incompatible_types']],
    'complex_destructuring':
        [dedent("""
                class Player:
                    def __init__(self):
                        self.health = 100
                class World:
                    def __init__(self):
                        self.p = Player()
                w = World()
                w.p.health, w.p = (5, Player())
                """), ['incompatible_types'], []],
    'class_type_promotion':
        [dedent("""
                class Enemy:
                    def __init__(self):
                        self.health = 0
                class Player:
                    def __init__(self):
                        self.enemies = []
                class World:
                    def __init__(self):
                        self.p = Player()
                w = World()
                w.p.enemies.append(Enemy())
                w.p.enemies[0].health + 100
                """), ['incompatible_types'], []],

    # Mutable Types
    'mutable_list_in_function':
        ['def t():\n    x = []\n    x.append(1)\n    return x\nfor x in t():\n    x + 1', ['incompatible_types'], []],
    # Importing
    'import_matplotlib':
        ['import matplotlib.pyplot as plt\nplt.hist([1,2,3])\nplt.show()', ['initialization_problem'], []],
    'import_random':
        ['from random import randint\na=randint(1,2)\n1+a', ['initialization_problem', 'incompatible_types'], []],

    'import_state_demographics':
        [
            "import state_demographics\n\n\nincome_list = state_demographics.get(\"Per Capita Income\",\"(None)\",'')\nfilter_income = []\nfor income in income_list:\n    if income > 28000:\n        income_list.append(filter_income)\nprint(filter_income)\n",
            [], []],
    'import_state_demographics2':
        [
            "import state_demographics\n\n\nincome_list = state_demographics.get(\"Per Capita Income\",\"(None)\",'')\nnew_income_list = 0\nfor income in income_list:\n    if income > 28000:\n        new_income_list = new_income_list + 1\nprint(new_income_list)\n",
            [], []],
    'filter_pattern':
        ['l = []\nfor x in l:\n    if x > 0:\n        x', [], []],
    'append_iter_var_to_list':
        ['x = []\nx.append(x)\nx', [], []],
    'append_multiple_types':
        ['x = []\nx.append(7)\nx.append("F")\nx', [], ['type_change_append']],
    'bad_append_iter_var_to_list':
        ['x = []\nx.append(x)\nx.append(7)\nx', [], ['type_change_append']],
    'function_with_parameter':
        ['def x(y):\n    y\nx()', [], []],
    'function_returns_None':
        ['def x():\n    return\nx()', [], []],
    'mutually_recursive_call':
        ['def y():\n    x()\ndef x():\n    y()\nx()', [], ['recursive_call']],
    'recursive_call':
        ['def x():\n    x()\nx()', [], ['recursive_call']],
    'overwritten_double_nested_branch':
        ['b= 0\nif True:\n    if True:\n        b=0\nb', ['possible_initialization_problem'], []],
    # Overwritten in one branches
    'overwritten_in_one_branch_alt':
        ['a = 0\nif True:\n\ta = 1\na', ['possible_initialization_problem'], []],
    'filter_pattern2':
        ["t = 0\nfor x in []:\n    if x:\n        t = t + 1\nprint(t)", ['possible_initialization_problem'], []],
    'read_out_scope2':
        ["x = ''\ndef y():\n    return x\ny()", ['unused_variable'], []],

    'read_out_scope_double_branch':
        ["def x():\n  if True:\n    y=0\n  else:\n    y=1\n  y\nx()",
         ['unused_variable', 'read_out_of_scope'], []],

    # Calling functions from within functions
    'call_function_within_function':
        ['def z():\n     return b\ndef y():\n    b = 0\n    z()\n    return b\ndef x():\n    y()\nx()',
         ['unused_variable'], ['read_out_of_scope']],

    # While loop with possibly unused body
    'while_body_and_conditional_uses_variable':
        ['a = 10\nwhile a:\n    a -= 1', ['unused_variable'], []],
    'while_body_uses_variable':
        ['a = 10\nwhile True:\n    a -= 1', [], ['unused_variable']],
    'while_body_possibly_defines_variable':
        ['while True:\n    a=0\na', [], ['possible_initialization_problem']],
    'while_body_defined_variable':
        ['a=0\nwhile True:\n    a=0\na', ['possible_initialization_problem'], []],

    # Generators
    'add_list_to_list_comprehension':
        ['[1]+[a for a in [1,2,3]]', ['unused_variable', "incompatible_types"], []],
    'add_set_to_set_comprehension':
        ['{4}+{a for a in [1,2,3]}', ['unused_variable'], ["incompatible_types"]],
    'union_set_to_set_comprehension':
        ['{4}|{a for a in [1,2,3]}', ['unused_variable', "incompatible_types"], []],
    'int_membership_in_dictionary':
        ['3 in {a:a for a in [1,2,3]}', ['unused_variable', "incompatible_types"], []],
    'int_membership_in_comprehension':
        ['4 in (a for a in [1,2,3])', ['unused_variable', "incompatible_types"], []],

    'prevent_empty_iteration_in_appended_list':
        ['eles = [1,2,3]\nx = []\nfor ele in eles:\n    x.append(ele)\nfor e2 in x:\n    e2+1',
         ['iterating_over_empty_list'], []],

    'prevent_empty_iteration_dict':
        ['x={"A":5}\nfor y in x:\n y', ['iterating_over_empty_list'], []],
    
    # Slices
    'function_call_in_slice':
        ['def x(): return 2\n"TEST"[:x()]', ['unused_variable'], []],

    # Built-in modules
    'import_string_letters':
        ['import string\nstring.letters+""', ['incompatible_types'], []],

    # Nested function definitions
    'function_nested_inside_if':
        ['if False:\n  def x():\n    pass', [], ['nested_function_definition']],
    'function_toplevel':
        ['def x():\n  if False:\n    pass', ['nested_function_definition'], []],
    'no_function_whatsoever':
        ['if False:\n  pass', ['nested_function_definition'], []],
    'unused_result_function':
        ['abs(-5)', [], ['unused_returned_value']],
    'unused_result_method':
        ['"".strip()', [], ['unused_returned_value']],
    'unused_result_custom_function':
        ['def x(): return 7\nx()', [], ['unused_returned_value']],
    'used_result_custom_function':
        ['def x(): return 7\nprint(x())', ['unused_returned_value'], []],
    'used_result_function':
        ['print(abs(-5))', ['unused_returned_value'], []],

    # Reused variable in outer scope
    'function_reused_outer_variable_write':
        ['def y(b): return b+"!"\ndef x(a): return y(a)+"?"\na="Hi"\nx(a)',
         ['write_out_of_scope'], []],

    # Dictionary stuff
    'dictionary_literal_key_access_int':
        ['person = {"Name": "Charles", "Age": 4}\nperson["Age"] + 1',
         ['incompatible_types'], []],
    'dictionary_literal_key_access_int_bad':
        ['person = {"Name": "Charles", "Age": 4}\nperson["Age"] + "1"',
         [], ['incompatible_types']],
    'dictionary_literal_key_access_str':
        ['person = {"Name": "Charles", "Age": 4}\nperson["Name"] + 1',
         [], ['incompatible_types']],
    'dictionary_literal_key_access_str_bad':
        ['person = {"Name": "Charles", "Age": 4}\nperson["Name"] + "1"',
         ['incompatible_types'], []],

    # Enumerate
    'enumerate_function_in_function':
        ['def do_it(data):\n    v = 0\n    for i, _ in enumerate(data):\n        v += i\n    return v\ndo_it("ab")',
         ['unused_variable'], []],
}


class TestCode(unittest.TestCase):
    pass


SILENCE_EXCEPT = None #'enumerate_function_in_function' # 'possibly_overwritten_in_elif_branch' # None  # 'read_not_out_of_scope'


def make_tester(internal_name, code, nones, somes):
    def test_code(self):
        contextualize_report(code)
        tifa = pedal.tifa.Tifa()
        try:
            result = tifa.process_code(code)
        except Exception as e:
            raise type(e)(str(e) +
                          ' in code:\n%s' % code)
        if not result.success:
            traceback.print_tb(result.error.__traceback__)
            #self.fail("Error message in\n" + code + "\n" +
            #          str(result.error))
            self.fail(f"Error occurred: {str(result.error)}\nName: {internal_name}\n----\n{code}\n----\n")
        for none in nones:
            if result.issues.get(none, []):
                print("")
                pprint(result.variables)
                self.fail(f"Incorrectly detected `{none}`\nName: {internal_name}\n----\n{code}\n----\n")
        for some in somes:
            if not result.issues.get(some, []):
                self.fail(f"Failed to detect `{some}`\nName: {internal_name}\n----\n{code}\n----\n")
    test_code.__name__ = "test_code_"+str(internal_name)
    return test_code


for name, (code, nones, somes) in unit_tests.items():
    if SILENCE_EXCEPT in (None, "None") or SILENCE_EXCEPT == name:
        setattr(TestCode, 'test_code_{}'.format(name), make_tester(name, code, nones, somes))


class TestVariables(unittest.TestCase):
    def test_type_comparisons(self):
        tifa = pedal.tifa.Tifa()
        result = tifa.process_code('my_int=0\nmy_str="A"\nmy_list=[1,2,3]')
        variables = result.top_level_variables
        self.assertEqual(len(variables), 3)
        # Integer variable
        my_int = variables['my_int'].type
        self.assertTrue(my_int.is_equal('num'))
        self.assertTrue(my_int.is_equal('NumType'))
        self.assertTrue(my_int.is_equal(int))
        self.assertFalse(my_int.is_equal(float))
        self.assertFalse(my_int.is_equal(str))
        # String variable
        my_str = variables['my_str'].type
        self.assertTrue(my_str.is_equal('str'))
        self.assertTrue(my_str.is_equal('StrType'))
        self.assertTrue(my_str.is_equal(str))
        # List variable
        my_list = variables['my_list'].type
        self.assertTrue(my_list.is_equal('list'))
        self.assertTrue(my_list.is_equal('ListType'))
        self.assertTrue(my_list.is_equal(list))
        # List subtype
        self.assertTrue(my_list.element_type.is_equal(int))
        self.assertTrue(my_list.element_type.is_equal('num'))
        self.assertFalse(my_list.element_type.is_equal(float))
        self.assertTrue(my_list.element_type.is_equal('NumType'))

    def test_variable_def_use(self):
        tifa = pedal.tifa.Tifa()
        result = tifa.process_code('a=0\nb=0\nb\nc')
        issues = result.issues
        # Unused variables
        self.assertEqual(len(issues['unused_variable']), 1)
        unused_variables = [i.fields['name'] for i in issues['unused_variable']]
        self.assertIn('a', unused_variables)
        self.assertNotIn('b', unused_variables)
        self.assertNotIn('c', unused_variables)
        # Uninitalized variables
        self.assertEqual(len(issues['initialization_problem']), 1)
        unset_variables = [i.fields['name'] for i in issues['initialization_problem']]
        self.assertNotIn('a', unset_variables)
        self.assertNotIn('b', unset_variables)
        self.assertIn('c', unset_variables)

    def test_weirdness_used_function(self):
        tifa = pedal.tifa.Tifa()
        result = tifa.process_code('def a(x):\n    return x\na(1)')
        self.assertTrue(result.success)

        tifa = pedal.tifa.Tifa()
        result = tifa.process_code('def a(x):\n    return x\n')
        issues = result.issues
        self.assertEqual(issues['unused_variable'][0].message,
                         "The function a was "
                         "given a definition on line 1, but was never used "
                         "after that.")

    def test_bad_parameter_found(self):
        tifa = pedal.tifa.Tifa()
        result = tifa.process_code('def a(x: int):\n    return x\na("hello")')
        issues = result.issues
        self.assertEqual(issues['parameter_type_mismatch'][0].message,
                         "You defined the parameter x as an integer. However, the argument passed to that parameter on line 3 was a string. The formal parameter type must match the argument's type.")

    def test_bad_parameter_found_complex(self):
        tifa = pedal.tifa.Tifa()
        result = tifa.process_code('def a(x: list[int]):\n    return x\na(5)')
        issues = result.issues
        self.assertEqual(issues['parameter_type_mismatch'][0].message,
                         "You defined the parameter x as a list of integers. However, the argument passed to that parameter on line 3 was an integer. The formal parameter type must match the argument's type.")

    def test_weirdness_tate_import_example(self):
        tifa = pedal.tifa.Tifa()
        result = tifa.process_code(dedent('''
        import tate
        art = tate.get_artwork()
        h = [a['dimensions']['height'] for a in art if a['artist']['birth']['year'] > 1000]
        b = [a['artist']['birth']['year'] for a in art 
             if a['artist']['birth']['year'] > 1000]
        import matplotlib.pyplot as plt
        plt.scatter(b, h, alpha=.1)
        plt.show()'''))
        self.assertTrue(result.success)

    '''
    def test_tifa_graceful_errors(self):
        student_code = '1 + "Banana"'
        set_source(student_code)
        exception = commands.run_student()
        self.assertIsNotNone(exception)'''

    def test_json_types(self):
        t = normalize.get_pedal_type_from_json({'type': 'NumType'})
        self.assertIsInstance(t, defs.NumType)
        t = normalize.get_pedal_type_from_json({'type': 'StrType'})
        self.assertIsInstance(t, defs.StrType)
        t = normalize.get_pedal_type_from_json({'type': 'BoolType'})
        self.assertIsInstance(t, defs.BoolType)
        t = normalize.get_pedal_type_from_json({'type': 'NoneType'})
        self.assertIsInstance(t, defs.NoneType)
        t = normalize.get_pedal_type_from_json({'type': 'ListType',
                                 'subtype': {'type': 'NumType'}})
        self.assertIsInstance(t, defs.ListType)
        self.assertIsInstance(t.element_type, defs.NumType)

        l1 = {'type': 'LiteralStr', 'value': 'First'}
        l2 = {'type': 'LiteralStr', 'value': 'Second'}
        v1, v2 = {'type': 'StrType'}, {'type': 'NumType'}
        t = normalize.get_pedal_type_from_json({'type': 'DictType', 'literals': [l1, l2],
                                 'values': [v1, v2]})
        self.assertIsInstance(t, defs.DictType)
        self.assertIsInstance(t.element_types, list)
        self.assertEqual(len(t.element_types), 2)
        self.assertIsInstance(t.element_types[0][0], defs.LiteralStr)
        self.assertEqual(t.element_types[0][0].value, 'First')
        self.assertIsInstance(t.element_types[1][0], defs.LiteralStr)
        self.assertEqual(t.element_types[1][0].value, 'Second')
        self.assertIsInstance(t.element_types, list)
        self.assertEqual(len(t.element_types), 2)
        self.assertIsInstance(t.element_types[0][1], defs.StrType)
        self.assertIsInstance(t.element_types[1][1], defs.NumType)

        # Try to parse the Broadway type definition
        complex_type = {"type": "ModuleType",
                        "fields": {
                            'get': {"type": "ListType", "empty": False,
                                    "subtype": {"type": "NumType"}},

                            'get_shows':
                                {"type": "ListType", "subtype":
                                    {"type": "DictType", "literals": [{"type": "LiteralStr", "value": 'Statistics'},
                                                                      {"type": "LiteralStr", "value": 'Show'},
                                                                      {"type": "LiteralStr", "value": 'Date'}],
                                     "values": [
                                         {"type": "DictType", "literals": [{"type": "LiteralStr", "value": 'Capacity'},
                                                                           {"type": "LiteralStr",
                                                                            "value": 'Attendance'},
                                                                           {"type": "LiteralStr",
                                                                            "value": 'Performances'},
                                                                           {"type": "LiteralStr", "value": 'Gross'},
                                                                           {"type": "LiteralStr",
                                                                            "value": 'Gross Potential'}], "values": [
                                             {"type": "NumType"},
                                             {"type": "NumType"},
                                             {"type": "NumType"},
                                             {"type": "NumType"},
                                             {"type": "NumType"}]},
                                         {"type": "DictType", "literals": [{"type": "LiteralStr", "value": 'Type'},
                                                                           {"type": "LiteralStr", "value": 'Theatre'},
                                                                           {"type": "LiteralStr", "value": 'Name'}],
                                          "values": [
                                              {"type": "StrType"},
                                              {"type": "StrType"},
                                              {"type": "StrType"}]},
                                         {"type": "DictType", "literals": [{"type": "LiteralStr", "value": 'Day'},
                                                                           {"type": "LiteralStr", "value": 'Month'},
                                                                           {"type": "LiteralStr", "value": 'Year'},
                                                                           {"type": "LiteralStr", "value": 'Full'}],
                                          "values": [
                                              {"type": "NumType"},
                                              {"type": "NumType"},
                                              {"type": "NumType"},
                                              {"type": "StrType"}]}]}},

                        }}
        normalize.get_pedal_type_from_json(complex_type)

    def test_custom_module_import_weather(self):
        tifa = pedal.tifa.Tifa()
        result = tifa.process_code('import weather\n' +
                          'rs = weather.get_weather()\n' +
                          'for r in rs:\n' +
                          '  0+r["Data"]["Precipitation"]',
                                   filename='student.py')
        self.assertTrue(result.success)
        self.assertNotIn('module_not_found', result.issues)

    def test_custom_module_import_police(self):
        tifa = pedal.tifa.Tifa()
        result = tifa.process_code('import police_shootings\n'
                          'rs = police_shootings.get_shootings()\n'
                          'for r in rs:\n'
                          '  x=0+r["Person.Age"]\n'
                          'x', filename='student.py')
        self.assertTrue(defs.is_subtype(result.top_level_variables['x'].type, defs.NumType()))
        self.assertTrue(result.success)
        self.assertNotIn('module_not_found', result.issues)

    def test_custom_module_import_babbages(self):
        tifa = pedal.tifa.Tifa()
        result = tifa.process_code('import babbages\n'
                          'print(babbages)', filename='student.py')
        self.assertIn('module_not_found', result.issues)

    def test_custom_module_import_broadway(self):
        tifa = pedal.tifa.Tifa()
        result = tifa.process_code(dedent("""
            import broadway
            report_list = broadway.get_shows()
            total= 0
            for broadway in report_list:
                if broadway ["Show"]["Type"] == "Musical":
                    total = total + 1
            print(total)"""), filename='student.py')
        self.assertTrue(result.success)
        self.assertNotIn('module_not_found', result.issues)

    def test_get_types(self):
        tifa = pedal.tifa.Tifa()
        result = tifa.process_code('a=0\na="Hello"\na=[1,2,3]\na=1')
        a = result.top_level_variables['a']
        self.assertTrue(a.was_type('num'))
        self.assertTrue(a.was_type(int))
        self.assertTrue(a.was_type('NumType'))
        self.assertTrue(a.was_type(defs.NumType))
        self.assertFalse(a.was_type(bool))
        self.assertFalse(a.was_type(defs.DictType))
        self.assertTrue(a.was_type('ListType'))

        tifa = pedal.tifa.Tifa()
        result = tifa.process_code('credits=[1,2,3,4]\nfor credit in credits:\n  print(credit)')
        credit = result.top_level_variables['credit']
        self.assertFalse(credit.was_type(list))
        self.assertTrue(credit.was_type(int))

    def test_dict_iteration(self):
        tifa = pedal.tifa.Tifa()
        result = tifa.process_code('dict = {"T": 0}\nfor i in dict:\n    print(i, dict[i])')
        self.assertTrue(result.success)

    def test_classes(self):
        program = 'class A:\n def __init__(self):\n  self.x=0\na=A()\na.x+""'
        # print(indent(program, '    '))
        tifa = pedal.tifa.Tifa()
        result = tifa.process_code(program)
        # self.assertTrue(tifa.report['tifa']['success'])
        # pprint(tifa.report['tifa'])
        # print(tifa.report['tifa']['top_level_variables']['a'].type.parent.fields)
        self.assertFalse(result.error)

        program = dedent("""
                class Enemy:
                    def __init__(self):
                        self.health = 0
                class Player:
                    def __init__(self):
                        self.enemies = []
                class World:
                    def __init__(self):
                        self.p = Player()
                w = World()
                w.p.enemies.append(Enemy())
                w.p.enemies[0].health + 100
                """)
        tifa = pedal.tifa.Tifa()
        tifa.process_code(program)
        # pprint(tifa.report['tifa'])
    
    def test_locations(self):
        program = dedent("""
                a = 0
                "Ignore"
                "This"
                "Line"
                def unnecessary():
                    pass
                unnecessary
                """)
        tifa = pedal.tifa.Tifa()
        result = tifa.process_code(program)
        self.assertEqual(result.issues['unused_variable'][0].location.line, 2)


    def test_weird_indexing_behavior(self):
        program = dedent("""
        movie_list = [{'Title':'Iron Man', 'Release Date':'May 2, 2008','Budget':'140','Running Time':'126'},
              {'Title':'Iron Man 2', 'Release Date':'May 7, 2010','Budget':'200', 'Running Time':'125'},
              {'Title':'Iron Man 3', 'Release Date':'May 3, 2013','Budget':'200', 'Running Time':'130'}]
        total=0
        for title in movie_list:
            total=total + 'title'['Running Time']
        print(total)
        """)
        tifa = pedal.tifa.Tifa()
        result = tifa.process_code(program)
        #self.assertNotIn('incompatible_types', result.issues)
        self.assertIn('invalid_indexing', result.issues)

    def test_not_finding_unused_return_value(self):
        program = dedent("""
            #import classics
            import matplotlib.pyplot as plt
            book_downloads = []
            #report_list = classics.get_books(test=True)
            report_list = [{'bibliography': {'type': 'Text'},
                            'metadata': {'downloads': 0}}]
            for report in report_list:
                if report["bibliography"]["type"] == "Text":
                    book_downloads.append(report["metadata"]["downloads"])
            plt.hist(book_downloads)
            plt.ylabel("Number of Books")
            plt.xlabel("downloads")
            plt.title("Spreads of Book Downloads")
            plt.show()
        """)
        tifa = pedal.tifa.Tifa()
        result = tifa.process_code(program, filename="student.py")
        self.assertNotIn('unused_returned_value', result.issues)
        self.assertFalse(result.issues)

    @unittest.skip("Currently broken, need to increase sophistication of typeddict support")
    def test_typedict_book(self):
        program = dedent("""
            from cisc108 import *
            class Book(TypedDict):
                title: str
                pages: int
                hardcover: bool
            
            def page_count(a_book: Book) -> int:
                return a_book['pages']
                
            hp = {'title': 'Harry Potter',
                  'pages': 300,
                  'hardcover': false}
            
            assert_equal(page_count(hp), 300)
        """)
        tifa = pedal.tifa.Tifa()
        result = tifa.process_code(program, filename="student.py")
        self.assertFalse(result.issues)

    def test_unnecessary_second_branch(self):
        program = dedent("""# Remember to initialize the variables!
age = 20
has_license = True
# Keep this If/else structure unchanged, but
# fill in the blanks with the code above
if has_license == True:
    if age >= 21:
        print("Can drink")
        if age < 1000:
            pass
        else:
            print("Too old")
            
    else:
        print("Too young")
        
else:
    print("Doesn't have a license")""")
        tifa = pedal.tifa.Tifa()
        result = tifa.process_code(program, filename="student.py")
        self.assertTrue(result.issues)

    def test_complex_record_type(self):
        program = dedent("""
Test = {"a": str}

def x(y: [Test]):
    return y[0]['a']

print(x([{"a": "apple"}]))""")
        tifa = pedal.tifa.Tifa()
        result = tifa.process_code(program, filename="student.py")
        self.assertFalse(result.issues)

    def test_new_class_record_type(self):
        program = dedent("""
        from dataclasses import dataclass
        
        @dataclass
        class Dog:
            name: str
            age: int
            fuzzy: bool
            
        def is_fuzzy(a_dog: Dog) -> bool:
            return a_dog.fuzzy
            
        ada = Dog('Ada Bart', 4, True)
        print(ada.name)
        
        print(is_fuzzy(ada))
        """)
        tifa = pedal.tifa.Tifa()
        result = tifa.process_code(program, filename="student.py")
        self.assertFalse(result.issues)

    def test_new_class_record_type_bad_instance(self):
        program = dedent("""
        class Dog(record):
            name: str
            age: int
            fuzzy: bool

        def is_fuzzy(a_dog: Dog) -> bool:
            return a_dog.fuzzy

        ada = Dog('Ada Bart', 4)
        print(ada.name)

        print(is_fuzzy(ada))
        """)
        tifa = pedal.tifa.Tifa()
        result = tifa.process_code(program, filename="student.py")
        self.assertTrue(result.issues)

    def test_dataclass_mistake(self):
        program = dedent("""
        from dataclasses import dataclass
        
        @dataclass
        class Dog:
            name: str
            age: int
            fuzzy: bool
            
        @dataclass
        class Cat:
            name: str
            age: int
            fuzzy: bool

        def is_fuzzy(a_dog: Dog) -> bool:
            return a_dog.fuzzy

        ada = Dog('Ada Bart', 4, True)
        print(ada.name)

        print(is_fuzzy(ada))
        
        adacat = Cat("Ada Bart", 4, True)
        print(is_fuzzy(adacat))
        """)
        tifa = pedal.tifa.Tifa()
        result = tifa.process_code(program, filename="student.py")
        self.assertIsNone(result.error)
        self.assertTrue(result.issues)

    def test_dataclass_mistake_lists(self):
        program = dedent("""
        from dataclasses import dataclass

        @dataclass
        class Dog:
            name: str
            age: int
            fuzzy: bool

        @dataclass
        class Cat:
            name: str
            age: int
            fuzzy: bool

        def all_fuzzy(dogs: list[Dog]) -> bool:
            return all(a_dog.fuzzy for a_dog in dogs)

        ada = Dog('Ada Bart', 4, True)
        print(ada.name)

        print(all_fuzzy([ada]))

        adacat = Cat("Ada Bart", 4, True)
        print(all_fuzzy([adacat]))
        """)
        tifa = pedal.tifa.Tifa()
        result = tifa.process_code(program, filename="student.py")
        self.assertIsNone(result.error)
        self.assertTrue(result.issues)
        self.assertEqual("You defined the parameter dogs as a list of Dog. "
                         "However, the argument passed to that parameter on line 25 was a list of Cat. "
                         "The formal parameter type must match the argument's type.",
                         result.issues['parameter_type_mismatch'][0].message)

    def test_dataclass_bad_constructor_call_order(self):
        program = dedent("""
        from dataclasses import dataclass

        @dataclass
        class Dog:
            name: str
            age: int
            fuzzy: bool
        
        ada = Dog('Ada Bart', True, 4)
        print(ada.name)
        """)
        tifa = pedal.tifa.Tifa()
        result = tifa.process_code(program, filename="student.py")
        self.assertIsNone(result.error)
        self.assertTrue(result.issues)
        self.assertEqual("You defined the field age as an integer. However, the argument passed to that field's "
                         "parameter in the constructor function on line 10 was a boolean. The formal field type "
                         "must match the argument's type.",
                         result.issues['field_type_mismatch'][0].message)

    def test_dataclass_bad_constructor_call_arity(self):
        program = dedent("""
        from dataclasses import dataclass

        @dataclass
        class Dog:
            name: str
            age: int
            fuzzy: bool

        ada = Dog('Ada Bart', 4)
        print(ada.name)
        """)
        tifa = pedal.tifa.Tifa()
        result = tifa.process_code(program, filename="student.py")
        self.assertIsNone(result.error)
        self.assertTrue(result.issues)
        self.assertEqual("The constructor function Dog was given the wrong number of arguments. You should have "
                         "had 3 arguments, but instead you had 2 arguments.",
                         result.issues['incorrect_arity'][0].message)

    def test_dataclass_bad_constructor_call_extra(self):
        program = dedent("""
        from dataclasses import dataclass

        @dataclass
        class Dog:
            name: str
            age: int
            fuzzy: bool

        ada = Dog('Ada Bart', 4, True, "is cute!")
        print(ada.name)
        """)
        tifa = pedal.tifa.Tifa()
        result = tifa.process_code(program, filename="student.py")
        self.assertIsNone(result.error)
        self.assertTrue(result.issues)
        self.assertEqual("The constructor function Dog was given the wrong number of arguments. You should have "
                         "had 3 arguments, but instead you had 4 arguments.",
                         result.issues['incorrect_arity'][0].message)

    def test_import_second_file(self):
        main_program = dedent("""
        import monsters
        
        monsters.number + ""
        """)
        monster_file = dedent("""number = 7\nalpha = 'test'""")
        contextualize_report(Submission(files={'student.py': main_program, 'monsters.py': monster_file}))
        tifa = pedal.tifa.Tifa()
        result = tifa.process_code(main_program, filename="student.py")
        self.assertIsNone(result.error)
        self.assertTrue(result.issues)
        self.assertEqual("You used an addition operation with an integer and a string on line 4. But you can't do that with that operator. Make sure both sides of the operator are the right type.",
                         result.issues['incompatible_types'][0].message)
        self.assertEqual(len(result.issues.get('unused_variable', [])), 0)

    def test_import_second_file_successful(self):
        main_program = dedent("""
        from monsters import Monster, dracula

        dracula.name + ""
        print(Monster("Wolfman"))
        """)
        monster_file = dedent("""
        from dataclasses import dataclass
        @dataclass
        class Monster:
            name: str
        dracula = Monster('Dracula')""")
        contextualize_report(Submission(files={'student.py': main_program, 'monsters.py': monster_file}))
        tifa = pedal.tifa.Tifa()
        result = tifa.process_code(main_program, filename="student.py")
        self.assertIsNone(result.error)
        self.assertFalse(result.issues)

    def test_provide_import_type_definitions(self):
        main_program = dedent("""
        import monsters

        monsters.number + ""
        """)
        tifa = pedal.tifa.Tifa()
        tifa_provide_module_type('monsters', {'number': normalize.normalize_type('int')})
        result = tifa.process_code(main_program, filename="student.py")
        self.assertIsNone(result.error)
        self.assertTrue(result.issues)
        self.assertEqual(
            "You used an addition operation with an integer and a string on line 4. But you can't do that with that operator. Make sure both sides of the operator are the right type.",
            result.issues['incompatible_types'][0].message)

    @unittest.skip
    def test_provide_module_definitions(self):
        main_program = dedent("""
        from monsters import dracula

        dracula.age + ""
        """)
        tifa = pedal.tifa.Tifa()
        import tests.test_files.monsters as monsters
        tifa_provide_module_type('monsters', normalize.normalize_type(monsters))
        result = tifa.process_code(main_program, filename="student.py")
        if result.error is not None:
            raise result.error
        self.assertIsNone(result.error)
        self.assertTrue(result.issues)
        self.assertEqual(
            "You used an addition operation with an integer and a string on line 4. But you can't do that with that operator. Make sure both sides of the operator are the right type.",
            result.issues['incompatible_types'][0].message)

    def test_weird_return_control_flow(self):
        main_program = dedent("""
        from dataclasses import dataclass
        
        @dataclass
        class Media:
            name: str
            kind: str
            duration: int
        
        def longest(media: list[Media]) -> str:
            movies_only = [i for i in media if i.kind == 'movie']
            if not movies_only:
                return 'no movies'
            key = lambda movie: movie.duration
            return max(movies_only, key=key).name
        
        print(longest([Media("Snoopy", "movie", 5)]))
        print(longest([]))
        """)
        tifa = pedal.tifa.Tifa()
        result = tifa.process_code(main_program, filename="student.py")
        if result.error:
            raise result.error
        self.assertIsNone(result.error)
        self.assertFalse(result.issues)

    def test_weird_increment_set_list(self):
        main_program = dedent("""from dataclasses import dataclass

@dataclass
class Forecast:
    reports: list[int]
    
def rainfall(weather: list[Forecast]) -> list[int]:
    reports = []
    for a_weather in weather:
        reports += a_weather.reports
    return reports

def total_rainfall(forecast: list[Forecast]) -> int:
    total = 0
    reports = rainfall(forecast)
    for measurement in reports:
        total += measurement
    return total

forecast1 = [Forecast([1,2,3])]
5+total_rainfall(forecast1)""")
        tifa = pedal.tifa.Tifa()
        result = tifa.process_code(main_program, filename="student.py")
        if result.error:
            raise result.error
        self.assertIsNone(result.error)
        self.assertFalse(result.issues)

if __name__ == '__main__':
    unittest.main(buffer=False)

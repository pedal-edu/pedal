import unittest
import ast
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pedal.cait.cait_api import *


class CaitNodeTest(unittest.TestCase):
    def test_init_(self):
        program = ast.parse("fun = 0 + 1\nfun01 =  2 + 3\nfun02 = 4 + 5")
        program = CaitNode(program)
        second_assign = program.children[1]
        third_assign = program.children[2]
        self.assertTrue(second_assign == program.linear_tree[second_assign.tree_id], "Nodes not being index properly")
        self.assertTrue(third_assign == program.linear_tree[third_assign.tree_id], "Nodes not being index properly-2")

    def test_get_next_tree(self):
        program = ast.parse("fun = 0 + 1\nfun01 =  2 + 3\nfun02 = 4 + 5")
        program = CaitNode(program)
        first_assign_c = program.children[0]
        second_assign_c = program.children[1]
        third_assign_c = program.children[2]
        second_assign_test = first_assign_c.get_next_tree()
        with self.subTest():
            self.assertTrue(second_assign_test == second_assign_c, "next_tree not found, when it should be")
        with self.subTest():
            no_next_end = third_assign_c.get_next_tree()
            self.assertTrue(no_next_end is None, "next_tree found when it shouldn't be at end")

    def test_find_all(self):
        program = ast.parse(
            "\nmy_list = [1, 2, 3]\nif True:\n\tmy_list.append(4)\nfor item in my_list:\n\tif item == 1:"
            "\n\t\titem += 1\n\tif item == 2:\n\t\titem += 4\n\tif item == 3:\n\t\titem += 6")
        program = CaitNode(program)
        if_set = program.find_all("If")
        self.assertTrue(len(if_set) == 4, "Found {} ifs, when 4 should be found".format(len(if_set)))

        num_set = program.find_all("Num")
        self.assertTrue(len(num_set) == 10, "Found {} nums, when 10 should be found".format(len(num_set)))

        num_if_set = program.find_all(["Num", "If"])
        self.assertTrue(len(num_if_set) == 14, "Found {} nums, when 10 should be found".format(len(num_if_set)))

        for_node = program.children[2]
        if_set_for = for_node.find_all("If")
        self.assertTrue(len(if_set_for) == 3, "Found {} ifs, when 3 should be found".format(len(if_set_for)))

        if0_node = program.children[1]
        if_set_if0 = if0_node.find_all("If")
        self.assertTrue(len(if_set_if0) == 1, "Found {} ifs, when 1 should be found".format(len(if_set_if0)))

    def test_has(self):
        program = ast.parse("x\n"
                            "y\n"
                            "x = 0\n"
                            "y = 'fun'")
        program = CaitNode(program)
        x = program.body[0].value
        y = program.body[1].value
        line3 = program.body[2]
        line4 = program.body[3]
        self.assertTrue(line3.has(x))
        self.assertFalse(line3.has(y))
        self.assertTrue(line3.has(0))
        self.assertFalse(line3.has(1))
        self.assertTrue(line4.has("fun"))

    def test___getattr__(self):
        program = ast.parse("x = 0")
        program = CaitNode(program)
        self.assertTrue(program.ast_name == "Module", "Expected ast_name of 'Module', not{}".format(program.ast_name))

        assign = program.children[0]
        assign_value = assign.value
        self.assertTrue(assign_value.ast_name == "Num" or assign_value.ast_name == "Constant",
                        "__getattribute__ fallthrough failed")

        assign_targets = assign.targets
        self.assertTrue(type(assign_targets) == list, "expected list, got {} instead".format(list))

        assign_target = assign.target
        self.assertTrue(type(assign_target) == CaitNode, "Expected CaitNode, got {} instead".format(assign_target))

        program1 = ast.parse("0 < x < 1")
        program1 = CaitNode(program1)
        binops_node = program1.children[0].value

        binops_names = binops_node.ops_names
        binops_funcs = binops_node.ops
        self.assertTrue(type(binops_funcs) == list, "Expected list, got {} instead".format(type(binops_funcs)))
        self.assertTrue(type(binops_names) == list, "Expected list, got {} instead".format(type(binops_funcs)))
        self.assertTrue(isinstance(binops_funcs[0].astNode, ast.cmpop),
                        "Expected ast.cmpop, got {} instead".format(type(binops_funcs[0])))
        self.assertTrue(type(binops_names[0]) == str, "Expected ast.cmpop")

    @unittest.skip("Not implemented yet")
    def test_numeric_logic_check(self):
        program = CaitNode(ast.parse("if 24 < x < 35:\n"
                                     "    pass"))
        compare = program.linear_tree[2]
        self.assertTrue(compare.numeric_logic_check(1, "24 < x < 35"))
        self.assertFalse(compare.numeric_logic_check(1, "23 < x < 35"))

        program = CaitNode(ast.parse("if '24' < x < '35':\n"
                                     "    pass"))
        compare = program.linear_tree[2]
        self.assertFalse(compare.numeric_logic_check(1, "23 < x < 35"))

        program = CaitNode(ast.parse("20 < x and x < 25 or 15 < x and 15 < x < 32"))
        compare = program.body[0].value
        self.assertTrue(compare.numeric_logic_check(1, "20 < x < 25 or 15 < x < 32"))

        program = CaitNode(ast.parse("12*2 < x*55 + 36 < 55"))
        compare = program.body[0].value
        self.assertTrue(compare.numeric_logic_check(1, "-12 < x*55 < 55"))

        program = CaitNode(ast.parse("temperature >= 32 and temperature <= 50"))
        compare = program.body[0].value
        self.assertTrue(compare.numeric_logic_check(1, "32 <= temp <= 50"))

    def test_get_value(self):
        x_val = 0
        program = ast.parse("x = {x_val}".format(x_val=x_val))
        program = CaitNode(program)
        num_node = program.linear_tree[4]
        self.assertTrue(num_node.value == x_val,
                        ("get_value didn't function as intended "
                         "returned {} instead of {x_val}").format(
                            num_node.value, x_val=x_val))

        x_val = 1.7
        program = ast.parse("x = {x_val}".format(x_val=x_val))
        program = CaitNode(program)
        num_node = program.linear_tree[4]
        self.assertTrue(num_node.value == x_val,
                        ("get_value didn't function as intended "
                         "returned {} instead of {x_val}").format(
                            num_node.value, x_val=x_val))

        x_val = "'fun'"
        x_val_s = 'fun'
        program = ast.parse("x = {x_val}".format(x_val=x_val))
        program = CaitNode(program)
        str_node = program.linear_tree[4]
        self.assertTrue(str_node.value == x_val_s,
                        ("get_value didn't function as intended "
                         "returned {} instead of {x_val}").format(
                            str_node.value, x_val=x_val_s))

        x_val = False
        program = ast.parse("x = {x_val}".format(x_val=x_val))
        program = CaitNode(program)
        num_node = program.linear_tree[4]
        self.assertTrue(num_node.value == x_val,
                        ("get_value didn't function as intended "
                         "returned {} instead of {x_val}").format(
                            num_node.value, x_val=x_val))

        # TODO: Test .value for Name nodes

    def test_nested_expr_matching(self):
        student_code = ("my_sum = 0\n"
                        "for my_item in my_list:\n"
                        "    if True:\n"
                        "        my_sum = my_sum + my_item\n")
        pattern0 = ("for _item_ in _list_:\n"
                    "    __expr__")
        match01 = find_match(pattern0, student_code)
        self.assertTrue(match01)

        __expr__ = match01['__expr__']
        match02 = __expr__.find_match("___ = ___ + _item_")
        self.assertTrue(match02)

        # Case 2
        student_code = ("my_sum = 0\n"
                        "for my_item in my_list:\n"
                        "    if True:\n"
                        "        my_sum = my_sum + my_item2\n")
        pattern0 = ("for _item_ in _list_:\n"
                    "    __expr__")
        match01 = find_match(pattern0, student_code)
        self.assertTrue(match01)

        __expr__ = match01['__expr__']
        match02 = __expr__.find_match("___ = ___ + _item_")
        self.assertFalse(match02)

import unittest
import ast
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pedal.cait.easy_node import *


class EasyNodeTest(unittest.TestCase):
	def test_init_(self):
		program = ast.parse("fun = 0 + 1\nfun01 =  2 + 3\nfun02 = 4 + 5")
		program = EasyNode(program)
		second_assign = program.children[1]
		third_assign = program.children[2]
		self.assertTrue(second_assign == program.linear_tree[second_assign.tree_id], "Nodes not being index properly")
		self.assertTrue(third_assign == program.linear_tree[third_assign.tree_id], "Nodes not being index properly-2")

	def test_get_next_tree(self):
		program = ast.parse("fun = 0 + 1\nfun01 =  2 + 3\nfun02 = 4 + 5")
		program = EasyNode(program)
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
		program = ast.parse("\nmy_list = [1, 2, 3]\nif True:\n\tmy_list.append(4)\nfor item in my_list:\n\tif item == 1:"
							"\n\t\titem += 1\n\tif item == 2:\n\t\titem += 4\n\tif item == 3:\n\t\titem += 6")
		program = EasyNode(program)
		if_set = program.find_all("If")
		self.assertTrue(len(if_set) == 4, "Found {} ifs, when 4 should be found".format(len(if_set)))

		for_node = program.children[2]
		if_set_for = for_node.find_all("If")
		self.assertTrue(len(if_set_for) == 3, "Found {} ifs, when 3 should be found".format(len(if_set_for)))

		if0_node = program.children[1]
		if_set_if0 = if0_node.find_all("If")
		self.assertTrue(len(if_set_if0) == 1, "Found {} ifs, when 1 should be found".format(len(if_set_if0)))

	def test___getattr__(self):
		program = ast.parse("x = 0")
		program = EasyNode(program)
		self.assertTrue(program.ast_name == "Module", "Expected ast_name of 'Module', not{}".format(program.ast_name))

		assign = program.children[0]
		assign_value = assign.value
		self.assertTrue(assign_value.ast_name == "Num", "__getattribute__ fallthrough failed")

		assign_targets = assign.targets
		self.assertTrue(type(assign_targets) == list, "expected list, got {} instead".format(list))

		assign_target = assign.target
		self.assertTrue(type(assign_target) == EasyNode, "Expected EasyNode, got {} instead".format(assign_target))

		program1 = ast.parse("0 < x < 1")
		program1 = EasyNode(program1)
		binops_node = program1.children[0].value

		binops_names = binops_node.ops_names
		binops_funcs = binops_node.ops
		self.assertTrue(type(binops_funcs) == list, "Expected list, got {} instead".format(type(binops_funcs)))
		self.assertTrue(type(binops_names) == list, "Expected list, got {} instead".format(type(binops_funcs)))
		self.assertTrue(isinstance(binops_funcs[0], ast.cmpop), "Expected list, got {} instead".format(type(binops_funcs)))
		self.assertTrue(type(binops_names[0]) == str, "Expected ast.cmpop")
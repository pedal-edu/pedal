from __future__ import print_function
import unittest
import ast
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pedal.cait.stretchy_tree_matching import *
from pedal.cait.easy_node import *
from pedal.source import set_source
from pedal.tifa import tifa_analysis
from pedal.report import MAIN_REPORT, clear_report
from pedal.cait.cait_api import *

'''
_accu_ = 0
_iList_ = [1,2,3,4]
for _item_ in _iList_:
    accu_ = _accu_ + _item_
print(_accu_)
'''


def parse_code(student_code):
    """
    parses code and returns a new EasyNode that is the root of the student
    """
    return EasyNode(ast.parse(student_code))


class CaitTests(unittest.TestCase):

    def setUp(self):
        MAIN_REPORT.clear()

    def test_var_match(self):
        # print("TESTING VAR MATCH")
        # tests whether variables are stored correctly
        test_tree = StretchyTreeMatcher("_accu_ = 0")

        # extracting instrutor name node
        ins_ast = test_tree.rootNode
        ins_name_node = ins_ast.children[0].children[0]

        # creating student code
        student_code = "accumulator = 0"
        std_ast = parse_code(student_code)
        # extracting student name node
        std_name_node = std_ast.children[0].children[0]
        mapping = test_tree.shallow_match(ins_name_node, std_name_node)
        self.assertTrue(mapping, "match not found")

        if mapping:
            mapping = mapping[0]
            self.assertTrue(mapping.mappings.keys[0].astNode ==
                            ins_name_node.astNode, "ins node match not correct in _var_ case")
            self.assertTrue(mapping.mappings.values[0].astNode ==
                            std_name_node.astNode, "std node match not correct in _var_ case")
            debug_print = False  # TODO: debug flag
            if debug_print:
                print(test_tree)
                print(ins_name_node)
                print(std_name_node)
                print(mapping)

    def test_expresssion_match(self):
        # tests whether expressions are stored correctly
        # print("TESTING EXPRESSION MATCH")
        test_tree = StretchyTreeMatcher("__exp__ = 0")

        # extracting instrutor name node
        ins_ast = test_tree.rootNode
        ins_name_node = ins_ast.children[0].children[0]

        # creating student code
        student_code = "accumulator = 0\nfor item in myList:\n    accumulator += item"
        std_ast = parse_code(student_code)
        # extracting body node
        std_for_loop = std_ast.children[1]

        mapping = test_tree.shallow_match(ins_name_node, std_for_loop, False)
        self.assertTrue(mapping, "match not found")
        if mapping:
            mapping = mapping[0]
            if mapping:
                self.assertTrue(mapping.exp_table.keys[0] == "__exp__", "symbol match not found")
                self.assertTrue(mapping.exp_table.values[0].astNode == std_for_loop.astNode,
                                "did not match to correct ast node")
            debug_print = False  # TODO: debug flag
            if debug_print:
                print(test_tree)
                print(ins_name_node)
                print(std_for_loop)
                print(mapping)

    def test_wild_card_match(self):
        # tests whether Wild matches are stored correctly
        # print("TESTING WILD CARD MATCH")
        test_tree = StretchyTreeMatcher("___ = 0")

        # extracting instrutor name node
        ins_ast = test_tree.rootNode
        ins_name_node = ins_ast.children[0].children[0]

        # creating student code
        student_code = "accumulator = 0\nfor item in myList:\n    accumulator += item\nfor item in myList:" \
                       "\n    accumulator += item"
        std_ast = parse_code(student_code)
        # extracting body node
        std_for_loop = std_ast.children[1]
        mapping = test_tree.shallow_match(ins_name_node, std_for_loop, False)
        self.assertTrue(mapping, "match not found")
        if mapping:
            mapping = mapping[0]
            self.assertTrue(mapping.mappings.keys[0].astNode == ins_name_node.astNode and
                            mapping.mappings.values[0].astNode == std_for_loop.astNode, "wild card didn't match")
            debug_print = False  # TODO: debug flag
            if debug_print:
                print(test_tree)
                print(ins_name_node)
                print(std_for_loop)
                print(mapping)

    def test_match_all(self):
        # print("TESTING MATCH ALL")
        test_tree = StretchyTreeMatcher("___ = 0")
        ins_ast = test_tree.rootNode
        ins_num_node = ins_ast.children[0].children[1]

        # creating student code
        student_code = "billy = 0"
        std_ast = parse_code(student_code)
        # extracting body node
        std_num_node = std_ast.children[0].children[1]

        mapping = test_tree.shallow_match(ins_num_node, std_num_node)
        self.assertTrue(mapping, "match not found")
        if mapping:
            mapping = mapping[0]
            if mapping:
                self.assertTrue(mapping.mappings.keys[0].astNode == ins_num_node.astNode,
                                "ins node not matched correctly")
                self.assertTrue(mapping.mappings.values[0].astNode == std_num_node.astNode,
                                "student node not matched correctly")
            debug_print = False  # TODO: debug print
            if debug_print:
                print(test_tree)
                print(std_num_node)
                print(mapping)

    def test_generic_match(self):
        # print("TESTING SAME ORDER")
        std_code = "_sum = 0\n" \
                   "_list = [1,2,3,4]\n" \
                   "for item in _list:\n" \
                   "    _sum = _sum + item\n" \
                   "print(_sum)"
        ins_code = '_accu_ = 0\n' \
                   '_iList_ = __listInit__\n' \
                   'for _item_ in _iList_:\n' \
                   '    _accu_ = _accu_ + _item_\n' \
                   'print(_accu_)'
        # var std_code = "_sum = 12 + 13"
        # var ins_code = "_accu_ = 12 + 11"
        ins_tree = StretchyTreeMatcher(ins_code)
        ins_ast = ins_tree.rootNode
        std_ast = parse_code(std_code)

        mappings_array = ins_tree.find_matches(std_ast.astNode)
        self.assertTrue(mappings_array, "matches not found")
        if mappings_array:
            mappings = mappings_array[0]
            self.assertTrue(
                mappings.mappings.size() == len(ins_ast.linear_tree) - 1,  # -1 is because expression subsumes load
                "incorrect number of mappings found {} instead of {}".format(mappings.mappings.size(),
                                                                             len(ins_ast.linear_tree) - 1))
            self.assertTrue(mappings.symbol_table.size() == 3 and
                            len(mappings.symbol_table.values[0]) == 4 and
                            len(mappings.symbol_table.values[1]) == 2 and
                            len(mappings.symbol_table.values[2]) == 2, "inconsistent symbol matching")
            debug_print = False  # TODO: debug print
            if debug_print:
                print(mappings)
                print(ins_ast.astNode)
                print(std_ast.astNode)

    def test_many_to_one(self):
        # print("TESTING MANY TO ONE")
        std_code = "_sum = 0\nlist = [1,2,3,4]\n" \
                   "for item in list:\n" \
                   "    _sum = _sum + item\n" \
                   "print(_sum)"
        ins_code = "_accu_ = 0\n" \
                   "_iList_ = __listInit__\n" \
                   "for _item_ in _iList_:\n" \
                   "    _accu_ = _accu2_ + _item_\n" \
                   "print(_accu_)"
        ins_tree = StretchyTreeMatcher(ins_code)
        ins_ast = ins_tree.rootNode
        std_ast = parse_code(std_code)

        mappings = ins_tree.find_matches(std_ast.astNode)
        self.assertTrue(mappings, "no matches found")
        if mappings:
            mappings = mappings[0]
            if mappings:
                self.assertTrue(len(mappings.conflict_keys) == 0, "Conflicting keys when there shouldn't be")
                self.assertTrue(
                    mappings.symbol_table.size() == 4 and
                    len(mappings.symbol_table.values[0]) == 3 and
                    len(mappings.symbol_table.values[1]) == 2 and
                    len(mappings.symbol_table.values[2]) == 2 and
                    len(mappings.symbol_table.values[3]) == 1, "inconsistent symbol matching")
            debug_print = False
            if debug_print:
                print(ins_ast.astNode)
                print(std_ast.astNode)
                print(mappings)

    def test_commutativity(self):
        # print("TESTING COMMUTATIVITY ADDITION")
        # fail_count = 0
        # success_count = 0
        std_code = "_sum = 0\n" \
                   "list = [1,2,3,4]\n" \
                   "for item in list:\n" \
                   "    _sum = item + _sum\n" \
                   "print(_sum)"
        ins_code = "_accu_ = 0\n" \
                   "_iList_ = __listInit__\n" \
                   "for _item_ in _iList_:\n" \
                   "    _accu_ = _accu_ + _item_\n" \
                   "print(_accu_)"
        ins_tree = StretchyTreeMatcher(ins_code)
        ins_ast = ins_tree.rootNode
        std_ast = parse_code(std_code)

        mappings = ins_tree.find_matches(std_ast.astNode)
        self.assertTrue(mappings, "mapping not found")
        if mappings:
            mappings = mappings[0]
            self.assertTrue(mappings.conflict_keys != 0, "Conflicting keys in ADDITION when there shouldn't be")
            debug_print = False  # TODO: debug print
            if debug_print:
                print(ins_ast.astNode)
                print(std_ast.astNode)
                print(mappings)

    def test_one_to_many(self):
        # print("TESTING ONE TO MANY")
        std_code = "_sum = 0\n" \
                   "list = [1,2,3,4]\n" \
                   "for item in list:\n" \
                   "    _sum = _sum + _sum\n" \
                   "print(_sum)"
        ins_code = "_accu_ = 0\n" \
                   "_iList_ = __listInit__\n" \
                   "for _item_ in _iList_:\n" \
                   "    _accu_ = _accu_ + _item_\n" \
                   "print(_accu_)"
        ins_tree = StretchyTreeMatcher(ins_code)
        ins_ast = ins_tree.rootNode
        std_ast = parse_code(std_code)
        mappings = ins_tree.find_matches(std_ast.astNode)
        self.assertFalse(mappings, "found match when match shouldn't be found")
        debug_print = False  # TODO: debug print
        if debug_print:
            print(ins_ast.astNode)
            print(std_ast.astNode)
            print(mappings)

    def test_multimatch_false(self):
        # print("TESTING MULTI-MATCH")
        # var std_code = "_sum = 0\ncount = 0\nlist = [1,2,3,4]\nfor item in list:\n    _sum = _sum + item\n    count" \
        # " = count + 1\nprint(_sum)"
        std_code = "_sum = 0\n" \
                   "count = 0\n" \
                   "_list = [1,2,3,4]\n" \
                   "for item in _list:\n" \
                   "    _sum = _sum + count\n" \
                   "    count = _sum + count\n" \
                   "print(_sum) "
        ins_code = "_accu_ = 0\n" \
                   "_iList_ = __listInit__\n" \
                   "for _item_ in _iList_:\n" \
                   "    _accu_ = _accu_ + __exp__\n" \
                   "print(_accu_)"
        ins_tree = StretchyTreeMatcher(ins_code)
        ins_ast = ins_tree.rootNode
        std_ast = parse_code(std_code)
        mappings = ins_tree.find_matches(std_ast.astNode)
        self.assertFalse(len(mappings) > 1, "too many matches found")

        debug_print = False
        if debug_print:
            print(ins_ast)
            print(std_ast)
            print(mappings)

    def test_multimatch_true(self):
        std_code = "_sum = 0\n" \
                   "count = 0\n" \
                   "_list = [1,2,3,4]\n" \
                   "for item in _list:\n" \
                   "    _sum = _sum + count\n" \
                   "    count = _sum " \
                   "+ count\n" \
                   "print(_sum) "
        ins_code = "_accu_ = 0\n" \
                   "_iList_ = __listInit__\n" \
                   "for _item_ in _iList_:\n" \
                   "    _accu_ = _accu_ + __exp__"
        ins_tree = StretchyTreeMatcher(ins_code)
        ins_ast = ins_tree.rootNode
        std_ast = parse_code(std_code)
        mappings = ins_tree.find_matches(std_ast.astNode)
        self.assertTrue(len(mappings) >= 2, "Not enough mappings found")
        debug_print = False
        if debug_print:
            print(ins_ast)
            print(std_ast)
            print(mappings)

    def test_pass(self):
        # print("TESTING PASS MATCH")
        std_code = 'import matplotlib.pyplot as plt\n' \
                   'quakes = [1,2,3,4]\n' \
                   'quakes_in_miles = []\n' \
                   'for quakes in quakes:\n' \
                   '    quakes_in_miles.append(quake * 0.62)\n' \
                   'plt.hist(quakes_in_miles)\n' \
                   'plt.xlabel("Depth in Miles")\n' \
                   'plt.ylabel("Number of Earthquakes")\n' \
                   'plt.title("Distribution of Depth in Miles of Earthquakes")\n' \
                   'plt.show()'
        ins_code = "for _item_ in _item_:\n" \
                   "    pass"
        ins_tree = StretchyTreeMatcher(ins_code)
        ins_ast = ins_tree.rootNode
        std_ast = parse_code(std_code)
        mappings = ins_tree.find_matches(std_ast.astNode)
        self.assertTrue(mappings, "mapping should have been found")
        debug_print = False
        if debug_print:
            print(ins_ast)
            print(std_ast)
            print(mappings)

    def test_meta_stretch(self):
        # print("TESTING META STRETCH")
        std_code = ''.join([
            'steps_hiked_list = [1,2,3,4]\n',
            'total = 0\n',
            'for steps_hiked in steps_hiked_list:\n',
            '    total = steps_hiked + total\n',
            '    steps = steps + 1'])
        ins_code = "for ___ in ___:\n" \
                   "    ___ = _sum_ + ___"
        ins_tree = StretchyTreeMatcher(ins_code)
        ins_ast = ins_tree.rootNode
        std_ast = parse_code(std_code)
        mappings = ins_tree.find_matches(std_ast.astNode)
        self.assertTrue(mappings, "mapping should have been found")
        if mappings:
            self.assertTrue(len(mappings) == 3,
                            "Should find exactly 3 matches, instead found {count}".format(
                                count=len(mappings).__str__()))
        debug_print = False
        if debug_print:
            print(ins_ast)
            print(std_ast)
            print(mappings)

    def test_parse_program(self):
        # noinspection PyBroadException
        try:
            parse_program()
            self.assertTrue(False, "Program did not throw exception")
        except Exception:
            self.assertTrue(True, "Should NOT FAIL")
        set_source("fun = 1 + 0")
        parse_program()
        self.assertTrue('cait' in MAIN_REPORT, "No parsing happened")
    '''
    def test_def_use_error(self):
        set_source("fun = fun + 1")
        parse_program()
        name_node = MAIN_REPORT["source"]["ast"].body[0].easy_node.target
        self.assertTrue(def_use_error(name_node), "def_use error should have been found but wasn't")
        self.assertTrue(def_use_error("fun"), "def_use error should have been found but wasn't")
        self.assertFalse(def_use_error("gitax"), "variable doesn't exist")

    def test_data_type(self):
        set_source("fun = 1 + 1")
        parse_program()
        name_node = MAIN_REPORT["source"]["ast"].body[0].easy_node.target
        self.assertTrue(data_type(name_node).is_equal(int), "Data type not successfully found from name node")
        self.assertTrue(data_type("fun").is_equal(int), "Data type not successfully found from str name")'''

    def test_find_match(self):
        set_source("fun = 1 + 1")
        parse_program()
        match = find_match("_var_ = __expr__")
        self.assertTrue(type(match) == AstMap, "Match not found")

    def test_find_matches(self):
        set_source("fun = 1 + 1\nfun2 = 2 + 2")
        parse_program()
        matches = find_matches("_var_ = __expr__")
        self.assertTrue(type(matches) == list, "find_matches did not return a list")
        self.assertTrue(type(matches[0]) == AstMap, "find_matches does not contain an AstMap")
        self.assertTrue(len(matches) == 2, "find_matches does not return the correct number of matches")
    
    def test_invalid_code(self):
        set_source("float('0') + 1")
        parse_program()
        matches = find_match("_var_ = __expr__")
        self.assertIsNone(matches)

    def test_old_style_api(self):
        set_source("a = open('file.txt')")
        std_ast = parse_program()
        calls = std_ast.find_all("Call")
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].func.ast_name, 'Name')
        self.assertEqual(calls[0].func.id, 'open')
        self.assertEqual(len(calls[0].args), 1)
        
        clear_report()
        set_source("def a():\n  pass\na()")
        std_ast = parse_program()
        defs = std_ast.find_all("FunctionDef")
        self.assertEqual(len(defs), 1)

    def test_matches_in_matches(self):
        matcher1 = StretchyTreeMatcher("if __expr__:\n    pass")
        matcher2 = StretchyTreeMatcher("0.4*_item_")
        student_code = ("if 0.4*item < 40:\n"
                        "    pass")
        self.assertTrue(matcher2.find_matches(student_code, check_meta=False))
        matches = matcher1.find_matches(student_code)
        self.assertTrue(matches)

        __expr__ = matches[0].exp_table.get("__expr__")
        matches2 = find_expr_sub_matches("0.4*_item_", __expr__)
        self.assertTrue(matches2)


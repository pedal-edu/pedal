from __future__ import print_function
import unittest
import ast
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pedal.cait.stretchy_tree_matching import *
from pedal.cait.cait_node import *
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
    parses code and returns a new CaitNode that is the root of the student
    """
    return CaitNode(ast.parse(student_code))


class CaitTests(unittest.TestCase):

    def setUp(self):
        MAIN_REPORT.clear()

    def test_var_match(self):
        # print("TESTING VAR MATCH")
        # tests whether variables are stored correctly
        test_tree = StretchyTreeMatcher("_accu_ = 0", report=MAIN_REPORT)

        # extracting instrutor name node
        ins_ast = test_tree.root_node
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
            self.assertTrue(list(mapping.mappings.keys())[0].astNode ==
                            ins_name_node.astNode, "ins node match not correct in _var_ case")
            self.assertTrue(list(mapping.mappings.values())[0].astNode ==
                            std_name_node.astNode, "std node match not correct in _var_ case")
            debug_print = False  # TODO: debug flag
            if debug_print:
                print(test_tree)
                print(ins_name_node)
                print(std_name_node)
                print(mapping)

    def test_expression_match(self):
        # tests whether expressions are stored correctly
        # print("TESTING EXPRESSION MATCH")
        test_tree = StretchyTreeMatcher("__exp__ = 0", report=MAIN_REPORT)

        # extracting instructor name node
        ins_ast = test_tree.root_node
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
                keys = list(mapping.exp_table.keys())
                values = list(mapping.exp_table.values())
                self.assertTrue(keys[0] == "__exp__", "symbol match not found")
                self.assertTrue(values[0].astNode == std_for_loop.astNode,
                                "did not match to correct ast node")
            debug_print = False  # TODO: debug flag
            if debug_print:
                print(test_tree)
                print(ins_name_node)
                print(std_for_loop)
                print(mapping)

        student_code2 = ("for item in item_list:\n"
                         "    if item > 5:\n"
                         "        item_sum = item_sum + item")
        matcher1 = StretchyTreeMatcher("for ___ in ___:\n"
                                       "    __expr__", report=MAIN_REPORT)
        matches02 = matcher1.find_matches(student_code2)
        self.assertTrue(matches02, "Expression match doesn't match to subtree")

    def test_function_diving(self):
        # TODO: Fix this bug
        student_code1 = "print(report['station'])"
        student_code2 = "print(report['station']['city'])"

        matcher1 = StretchyTreeMatcher("___[__expr__]", report=MAIN_REPORT)

        matches01 = matcher1.find_matches(student_code1)
        matches02 = matcher1.find_matches(student_code2)

        self.assertTrue(matches01)
        self.assertTrue(matches02)

    def test_function_save(self):
        ins_code = ("def _my_func_():\n"
                    "   pass")
        std_code = ("def funky(forum):\n"
                    "    pass")  # matches

        matcher = StretchyTreeMatcher(ins_code, report=MAIN_REPORT)
        matches = matcher.find_matches(std_code)

        self.assertTrue(matches, "did not match")
        table = matches[0].func_table
        keys = list(table.keys())
        self.assertTrue(len(keys) == 1, "found {} keys, should have found 1".format(len(keys)))
        self.assertTrue(keys[0] == '_my_func_',
                        "expected function name to be '_my_func_', found {} instead".format(keys[0]))

    def test_wild_card_match(self):
        # tests whether Wild matches are stored correctly
        # print("TESTING WILD CARD MATCH")
        test_tree = StretchyTreeMatcher("___ = 0", report=MAIN_REPORT)

        # extracting instrutor name node
        ins_ast = test_tree.root_node
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
            self.assertTrue(list(mapping.mappings.keys())[0].astNode == ins_name_node.astNode and
                            list(mapping.mappings.values())[0].astNode == std_for_loop.astNode, "wild card didn't match")
            debug_print = False  # TODO: debug flag
            if debug_print:
                print(test_tree)
                print(ins_name_node)
                print(std_for_loop)
                print(mapping)

    def test_match_all(self):
        # print("TESTING MATCH ALL")
        test_tree = StretchyTreeMatcher("___ = 0", report=MAIN_REPORT)
        ins_ast = test_tree.root_node
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
                self.assertTrue(list(mapping.mappings.keys())[0].astNode == ins_num_node.astNode,
                                "ins node not matched correctly")
                self.assertTrue(list(mapping.mappings.values())[0].astNode == std_num_node.astNode,
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
        ins_tree = StretchyTreeMatcher(ins_code, report=MAIN_REPORT)
        ins_ast = ins_tree.root_node
        std_ast = parse_code(std_code)

        mappings_array = ins_tree.find_matches(std_ast.astNode)
        self.assertTrue(mappings_array, "matches not found")
        if mappings_array:
            mappings = mappings_array[0]
            self.assertTrue(
                len(mappings.mappings) == len(ins_ast.linear_tree) - 1,  # -1 is because expression subsumes load
                "incorrect number of mappings found {} instead of {}".format(len(mappings.mappings),
                                                                             len(ins_ast.linear_tree) - 1))
            self.assertEqual(len(mappings.symbol_table), 3, "inconsistent symbol matching")
            lengths = sorted([len(v) for v in mappings.symbol_table.values()])
            self.assertEqual(lengths, [2, 2, 4], "inconsistent symbol matching")
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
        ins_tree = StretchyTreeMatcher(ins_code, report=MAIN_REPORT)
        ins_ast = ins_tree.root_node
        std_ast = parse_code(std_code)

        mappings = ins_tree.find_matches(std_ast.astNode)
        self.assertTrue(mappings, "no matches found")
        if mappings:
            mappings = mappings[0]
            if mappings:
                self.assertTrue(len(mappings.conflict_keys) == 0, "Conflicting keys when there shouldn't be")
                self.assertEqual(len(mappings.symbol_table), 4, "inconsistent symbol matching")
                lengths = sorted([len(v) for v in mappings.symbol_table.values()])
                self.assertEqual(lengths, [1, 2, 2, 3], "inconsistent symbol matching")
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
        ins_tree = StretchyTreeMatcher(ins_code, report=MAIN_REPORT)
        ins_ast = ins_tree.root_node
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
        ins_tree = StretchyTreeMatcher(ins_code, report=MAIN_REPORT)
        ins_ast = ins_tree.root_node
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
        ins_tree = StretchyTreeMatcher(ins_code, report=MAIN_REPORT)
        ins_ast = ins_tree.root_node
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
        ins_tree = StretchyTreeMatcher(ins_code, report=MAIN_REPORT)
        ins_ast = ins_tree.root_node
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
        ins_tree = StretchyTreeMatcher(ins_code, report=MAIN_REPORT)
        ins_ast = ins_tree.root_node
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
        ins_tree = StretchyTreeMatcher(ins_code, report=MAIN_REPORT)
        ins_ast = ins_tree.root_node
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
        name_node = MAIN_REPORT["source"]["ast"].body[0].cait_node.target
        self.assertTrue(def_use_error(name_node), "def_use error should have been found but wasn't")
        self.assertTrue(def_use_error("fun"), "def_use error should have been found but wasn't")
        self.assertFalse(def_use_error("gitax"), "variable doesn't exist")

    def test_data_type(self):
        set_source("fun = 1 + 1")
        parse_program()
        name_node = MAIN_REPORT["source"]["ast"].body[0].cait_node.target
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

        set_source("for 'fun' in ___:"
                   "if ___:\n"
                   "    pass")
        matches = find_matches("for ___ in ___:\n"
                               "    pass")
        self.assertFalse(matches, "find matches should have misparsed and returned False, but returned True instead")
    
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
        
        clear_report()
        set_source("1 < 1")
        std_ast = parse_program()
        compares = std_ast.find_all("Compare")
        self.assertEqual(len(compares), 1)
        
        clear_report()
        set_source("for x in y:\n  x")
        std_ast = parse_program()
        loops = std_ast.find_all("For")
        self.assertEqual(len(loops), 1)
        self.assertEqual(loops[0].target.ast_name, "Name")
        
        # Multiple assignment
        clear_report()
        set_source("a, b = 0, 1")
        std_ast = parse_program()
        assigns = std_ast.find_all("Assign")
        self.assertEqual(len(assigns), 1)
        self.assertEqual(len(assigns[0].targets), 1)
        self.assertEqual(assigns[0].targets[0].ast_name, 'Tuple')
        self.assertEqual(assigns[0].targets[0].elts[0].id, 'a')
        
        clear_report()
        set_source('from pprint import *')
        parse_program()

    def test_matches_in_matches(self):
        matcher1 = StretchyTreeMatcher("if __expr__:\n"
                                       "    pass", report=MAIN_REPORT)
        matcher2 = StretchyTreeMatcher("0.4*_item_", report=MAIN_REPORT)
        student_code = ("if 0.4*item < 40:\n"
                        "    pass")
        self.assertTrue(matcher2.find_matches(student_code, check_meta=False))
        matches = matcher1.find_matches(student_code)
        self.assertTrue(matches)

        __expr__ = matches[0]["__expr__"]
        matches2 = find_expr_sub_matches("0.4*_item_", __expr__)
        self.assertTrue(matches2)

        __expr__ = matches[0]["__expr__"]
        matches3 = find_expr_sub_matches(__expr__, __expr__)
        self.assertTrue(matches3)

    def test_symbol_mapping(self):
        student_code = ("item = 0\n"
                        "item2 = 1")
        matcher1 = StretchyTreeMatcher("_item_ = 0\n"
                                       "_item_ = 1", report=MAIN_REPORT)
        match = matcher1.find_matches(student_code)
        self.assertFalse(match, "One student variable is mapping to multiple instructor variables")

        student_code = ("item = 0\n"
                        "item = 1")
        matcher2 = StretchyTreeMatcher("_item_ = 0\n"
                                       "_item2_ = 1", report=MAIN_REPORT)
        match2 = matcher2.find_matches(student_code)
        self.assertTrue(match2, "One instructor variable should be able to map to multiple student variables, but isn't")

    def test_tree_cutting(self):
        student_code1 = ('maxtemp_list = []\n'
                         'mintemp_list = []\n'
                         'for report in weather_reports:\n'
                         '    if report["Station"]["City"] == "Blacksburg":\n'
                         '        maxtemp_list.append(report["Data"]["Temperature"]["Max Temp"])\n'
                         '        mintemp_list.append(report["Data"]["Temperature"]["Min Temp"])')

        student_parse = CaitNode(ast.parse(student_code1))
        matcher1 = StretchyTreeMatcher("'Blacksburg'", report=MAIN_REPORT)
        res = find_expr_sub_matches("'Blacksburg'", student_parse)
        self.assertTrue(res, "Cutting broke sub-matching")

        matches01 = matcher1.find_matches(student_code1)
        self.assertTrue(matches01, "Cutting doesn't work")

        student_code2 = ("def my_func(funky):\n"
                         "    print(funky)")
        matcher2 = StretchyTreeMatcher("def _func_def_():\n"
                                       "    pass", report=MAIN_REPORT)
        matches02 = matcher2.find_matches(student_code2)
        self.assertTrue(matches02, "Function reserved doesn't work with cutting")
        self.assertTrue(len(matches02[0].func_table.keys()) == 1, "Function node is ignored")

        student_code3 = "x"
        matcher3 = StretchyTreeMatcher("_x_", report=MAIN_REPORT)
        matches03 = matcher3.find_matches(student_code3)
        self.assertTrue(matches03, "Function reserved doesn't work with cutting")

    def test___getitem__(self):
        student_code2 = ("def my_func(funky):\n"
                         "    print(funky)")
        matcher2 = StretchyTreeMatcher("def _func_def_():\n"
                                       "    print(_funky_)", report=MAIN_REPORT)
        matches02 = matcher2.find_matches(student_code2)
        self.assertTrue(matches02, "match not found, aborting test")
        self.assertTrue(len(matches02[0].func_table.keys()) == 1, "improper number of keys, aborting test")
        self.assertTrue(matches02[0]['_func_def_'], "Couldn't retrieve function name.")
        self.assertTrue(matches02[0]['_funky_'], "Couldn't retrieve variable name.")

    @unittest.skip("Not yet implemented")
    def test_function_arg_matches(self):
        student_code2 = ("def my_func(funky):\n"
                         "    print(funky)")
        matcher2 = StretchyTreeMatcher("def _func_def_(_funky_):\n"
                                       "    pass", report=MAIN_REPORT)
        matches02 = matcher2.find_matches(student_code2)
        self.assertTrue(matches02, "match not found, aborting test")
        self.assertTrue(len(matches02[0].func_table.keys()) == 1, "improper number of keys, aborting test")
        self.assertTrue(matches02[0]['_func_def_'], "Couldn't retrieve function name.")
        self.assertTrue(matches02[0]['_funky_'], "Couldn't retrieve variable name.")
        
if __name__ == '__main__':
    unittest.main(buffer=False)

# from __future__ import print_function
import unittest
import ast
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pedal.cait.stretchy_tree_matching import *
from pedal.cait.cait_node import *
from pedal.source import set_source, verify
from pedal.tifa import tifa_analysis
from pedal.core.report import MAIN_REPORT
from pedal.core.commands import clear_report, contextualize_report
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
        """

        """
        MAIN_REPORT.clear()

    def test_var_match(self):
        """
        TODO: Things about symbols we haven't asked about
                - how does scope work? Right now everything is stored
                   in one name space because symbols don't currently
                   have an idea of "scope".
        Returns:

        """
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
                    "   pass\n"
                    "_my_func_()")
        std_code = ("def funky(forum):\n"
                    "    pass\n"
                    "funky(1200)")  # matches

        std_code2 = ("def funky(forum):\n"
                     "    pass\n"
                     "dunk(1200)")  # matches

        matcher = StretchyTreeMatcher(ins_code, report=MAIN_REPORT)
        matches = matcher.find_matches(std_code)

        self.assertTrue(matches, "did not match")
        table = matches[0].func_table
        keys = list(table.keys())
        self.assertTrue(len(keys) == 1, "found {} keys, should have found 1".format(len(keys)))
        self.assertTrue(keys[0] == '_my_func_',
                        "expected function name to be '_my_func_', found {} instead".format(keys[0]))
        self.assertTrue(len(table['_my_func_']) == 2, "function call and definition not counted as separate instances")

        matches2 = matcher.find_matches(std_code2)
        self.assertTrue(len(matches2) == 0, "Function calls and names aren't correlating")

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
                            list(mapping.mappings.values())[0].astNode == std_for_loop.astNode,
                            "wild card didn't match")
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
        std_code = ("_sum = 0\n"
                    "_list = [1,2,3,4]\n"
                    "for item in _list:\n"
                    "    _sum = _sum + item\n"
                    "print(_sum)")
        ins_code = ('_accu_ = 0\n'
                    '_iList_ = __listInit__\n'
                    'for _item_ in _iList_:\n'
                    '    _accu_ = _accu_ + _item_\n'
                    'print(_accu_)')
        # var std_code = "_sum = 12 + 13"
        # var ins_code = "_accu_ = 12 + 11"
        ins_tree = StretchyTreeMatcher(ins_code, report=MAIN_REPORT)
        ins_ast = ins_tree.root_node
        std_ast = parse_code(std_code)

        mappings_array = ins_tree.find_matches(std_ast.astNode)
        self.assertTrue(mappings_array, "matches not found")
        if mappings_array:
            mappings = mappings_array[0]
            self.assertTrue(len(mappings["_accu_"]) == 4, "Incorrect variable map")
            self.assertTrue(mappings["_accu_"].id == "_sum", "Incorrect variable map")

            self.assertTrue(len(mappings["_iList_"]) == 2, "Incorrect variable map")
            self.assertTrue(mappings["_iList_"].id == "_list", "Incorrect variable map")

            self.assertTrue(len(mappings["_item_"]) == 2, "Incorrect variable map")
            self.assertTrue(mappings["_item_"].id == "item", "Incorrect variable map")
            # _accu_/_sum is 4
            # _iList_/_list is 2
            # _item_/item is 2
            for k, v in mappings.mappings.items():
                try:
                    if k.id == "__lisetInit__":
                        self.assertTrue("List" == v.ast_name,
                                        "invalid mapping, {} mapped to {}".format(k.ast_name, v.ast_name))
                except AttributeError:
                    self.assertTrue(k.ast_name == v.ast_name,
                                    "invalid mapping, {} mapped to {}".format(k.ast_name, v.ast_name))
            debug_print = False  # TODO: debug print
            if debug_print:
                print(mappings)
                print(ins_ast.astNode)
                print(std_ast.astNode)

    def test_commutativity(self):
        # print("TESTING COMMUTATIVITY ADDITION")
        # fail_count = 0
        # success_count = 0
        std_code = ("_sum = 0\n"
                    "list = [1,2,3,4]\n"
                    "for item in list:\n"
                    "    _sum = item + _sum\n"
                    "print(_sum)")
        ins_code = ("_accu_ = 0\n"
                    "_iList_ = __listInit__\n"
                    "for _item_ in _iList_:\n"
                    "    _accu_ = _accu_ + _item_\n"
                    "print(_accu_)")
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

    def test_many_to_one(self):
        # print("TESTING MANY TO ONE")
        std_code = ("_sum = 0\nlist = [1,2,3,4]\n"
                    "for item in list:\n"
                    "    _sum = _sum + item\n"
                    "print(_sum)")
        ins_code = ("_accu_ = 0\n"
                    "_iList_ = __listInit__\n"
                    "for _item_ in _iList_:\n"
                    "    _accu_ = _accu2_ + _item_\n"
                    "print(_accu_)")
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

    def test_one_to_many(self):
        # print("TESTING ONE TO MANY")
        std_code = ("_sum = 0\n"
                    "list = [1,2,3,4]\n"
                    "for item in list:\n"
                    "    _sum = _sum + _sum\n"
                    "print(_sum)")
        ins_code = ("_accu_ = 0\n"
                    "_iList_ = __listInit__\n"
                    "for _item_ in _iList_:\n"
                    "    _accu_ = _accu_ + _item_\n"
                    "print(_accu_)")
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
        std_code = ("_sum = 0\n"
                    "count = 0\n"
                    "_list = [1,2,3,4]\n"
                    "for item in _list:\n"
                    "    _sum = _sum + count\n"
                    "    count = _sum + count\n"
                    "print(_sum) ")
        ins_code = ("_accu_ = 0\n"
                    "_iList_ = __listInit__\n"
                    "for _item_ in _iList_:\n"
                    "    _accu_ = _accu_ + __exp__\n"
                    "print(_accu_)")
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
        std_code = ("_sum = 0\n"
                    "count = 0\n"
                    "_list = [1,2,3,4]\n"
                    "for item in _list:\n"
                    "    _sum = _sum + count\n"
                    "    count = _sum "
                    "+ count\n"
                    "print(_sum) ")
        ins_code = ("_accu_ = 0\n"
                    "_iList_ = __listInit__\n"
                    "for _item_ in _iList_:\n"
                    "    _accu_ = _accu_ + __exp__")
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
        std_code = ('import matplotlib.pyplot as plt\n'
                    'quakes = [1,2,3,4]\n'
                    'quakes_in_miles = []\n'
                    'for quakes in quakes:\n'
                    '    quakes_in_miles.append(quake * 0.62)\n'
                    'plt.hist(quakes_in_miles)\n'
                    'plt.xlabel("Depth in Miles")\n'
                    'plt.ylabel("Number of Earthquakes")\n'
                    'plt.title("Distribution of Depth in Miles of Earthquakes")\n'
                    'plt.show()')
        ins_code = ("for _item_ in _item_:\n"
                    "    pass")
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
        contextualize_report("fun = 1 + 0")
        parse_program()
        self.assertTrue('cait' in MAIN_REPORT, "No parsing happened")

    """
    def test_def_use_error(self):
        contextualize_report("fun = fun + 1")
        parse_program()
        name_node = MAIN_REPORT["source"]["ast"].body[0].cait_node.target
        self.assertTrue(def_use_error(name_node), "def_use error should have been found but wasn't")
        self.assertTrue(def_use_error("fun"), "def_use error should have been found but wasn't")
        self.assertFalse(def_use_error("gitax"), "variable doesn't exist")

    def test_data_type(self):
        contextualize_report("fun = 1 + 1")
        parse_program()
        name_node = MAIN_REPORT["source"]["ast"].body[0].cait_node.target
        self.assertTrue(data_type(name_node).is_equal(int), "Data type not successfully found from name node")
        self.assertTrue(data_type("fun").is_equal(int), "Data type not successfully found from str name")"""

    def test_find_match(self):
        contextualize_report("fun = 1 + 1")
        parse_program()
        match = find_match("_var_ = __expr__")
        self.assertIsInstance(match, AstMap, "Match not found")

    def test_find_matches(self):
        contextualize_report("fun = 1 + 1\nfun2 = 2 + 2")
        parse_program()
        matches = find_matches("_var_ = __expr__")
        self.assertIsInstance(matches, list, "find_matches did not return a list")
        self.assertIsInstance(matches[0], AstMap, "find_matches does not contain an AstMap")
        self.assertEqual(len(matches), 2, "find_matches does not return the correct number of matches")

        contextualize_report("for 'fun' in ___:"
                             "if ___:\n"
                             "    pass")
        matches = find_matches("for ___ in ___:\n"
                               "    pass")
        self.assertFalse(matches, "find matches should have misparsed and returned False, but returned True instead")

    def test_invalid_code(self):
        contextualize_report("float('0') + 1")
        parse_program()
        matches = find_match("_var_ = __expr__")
        self.assertIsNone(matches)

    def test_old_style_api(self):
        contextualize_report("a = open('file.txt')")
        std_ast = parse_program()
        calls = std_ast.find_all("Call")
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].func.ast_name, 'Name')
        self.assertEqual(calls[0].func.id, 'open')
        self.assertEqual(len(calls[0].args), 1)

        clear_report()
        contextualize_report("def a():\n  pass\na()")
        std_ast = parse_program()
        defs = std_ast.find_all("FunctionDef")
        self.assertEqual(len(defs), 1)

        clear_report()
        contextualize_report("1 < 1")
        std_ast = parse_program()
        compares = std_ast.find_all("Compare")
        self.assertEqual(len(compares), 1)

        clear_report()
        contextualize_report("for x in y:\n  x")
        std_ast = parse_program()
        loops = std_ast.find_all("For")
        self.assertEqual(len(loops), 1)
        self.assertEqual(loops[0].target.ast_name, "Name")

        # Multiple assignment
        clear_report()
        contextualize_report("a, b = 0, 1")
        std_ast = parse_program()
        assigns = std_ast.find_all("Assign")
        self.assertEqual(len(assigns), 1)
        self.assertEqual(len(assigns[0].targets), 1)
        self.assertEqual(assigns[0].targets[0].ast_name, 'Tuple')
        self.assertEqual(assigns[0].targets[0].elts[0].id, 'a')

        clear_report()
        contextualize_report('from pprint import *')
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
        matches2 = __expr__.find_matches("0.4*_item_", )
        self.assertTrue(matches2)

        __expr__ = matches[0]["__expr__"]
        matches3 = __expr__.find_matches(__expr__, )
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
        self.assertTrue(match2,
                        "One instructor variable should be able to map to multiple student variables, but isn't")

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

    @unittest.skip("Does not support keyword arguments")
    def test_function_keyarg_matches(self):
        """
        TODO: This has a lot of aspects, such as
                - are keywords symbols that should be saved?
                - how are keywords stored in the name space?
                - how does that interact with the name space stuff
                    in variable matches?
        Returns:

        """
        self.assertTrue(False)

    def test_function_arg_matches(self):
        student_code2 = ("def my_func(funky):\n"
                         "    print(funky)")
        matcher2 = StretchyTreeMatcher("def _func_def_(_funky_):\n"
                                       "    pass", report=MAIN_REPORT)
        matches02 = matcher2.find_matches(student_code2)
        match02 = matches02[0]
        self.assertTrue(matches02, "match not found, aborting test")
        self.assertTrue(len(match02.func_table.keys()) == 1, "improper number of keys, aborting test")
        self.assertTrue(match02['_func_def_'], "Couldn't retrieve function name.")
        self.assertTrue(match02['_funky_'], "Couldn't retrieve variable name.")
        self.assertTrue(match02['_funky_'].id == "funky",
                        "Incorrect symbol name, expected 'funky' but got '{}' instead".format(match02['_funky_'].id))

        student_code3 = ("def my_func(funky, dunky):\n"
                         "    print(funky + dunky)")
        matcher3 = StretchyTreeMatcher("def _func_def_(_funky_, _funky2_):\n"
                                       "    pass", report=MAIN_REPORT)
        matches03 = matcher3.find_matches(student_code3)
        match03 = matches03[0]
        self.assertTrue(matches03, "match not found, aborting test")
        self.assertTrue(len(match03.func_table.keys()) == 1, "improper number of keys, aborting test")
        self.assertTrue(match03['_func_def_'], "Couldn't retrieve function name.")
        self.assertTrue(match03['_funky_'], "Couldn't retrieve variable name.")
        self.assertTrue(match03['_funky_'].id == "funky",
                        "Incorrect symbol name, expected 'funky' but got '{}' instead".format(match02['_funky_'].id))
        self.assertTrue(match03['_funky2_'], "Couldn't retrieve variable name.")
        self.assertTrue(match03['_funky2_'].id == "dunky",
                        "Incorrect symbol name, expected 'dunky' but got '{}' instead".format(match03['_funky_'].id))

    def test_cait_node_is_method(self):
        contextualize_report("class Dog:\n def bark(self):\n  pass\ndef dogs_bark(alod):\n pass")
        ast = parse_program()
        functions = ast.find_all('FunctionDef')
        self.assertTrue(functions[0].is_method())
        self.assertFalse(functions[1].is_method())
        classes = ast.find_all('ClassDef')
        self.assertFalse(classes[0].is_method())
        passes = ast.find_all('Pass')
        self.assertFalse(passes[0].is_method())
        self.assertFalse(passes[1].is_method())

    def test_ast_map_symbols(self):
        contextualize_report("fun = 0\nfun = 1")
        parse_program()
        my_match = find_match("_fun_ = ___")
        self.assertTrue(my_match["_fun_"].id == "fun")
        self.assertTrue(my_match["_fun_"][0].id == "fun")

    def test_function_Names(self):
        contextualize_report("import weather\n"
                             "weather_reports = get_weather('Data')\n"
                             "weather_reports = weather.get_weather('Data')\n"
                             "total = 0\n"
                             "for weather in weather_reports:\n"
                             "    total = total + weather\n"
                             "print(total)")
        parse_program()
        my_match = find_matches("_get_weather_(__expr__)")
        #  TODO: add to func table instead of symbol table?
        self.assertTrue(my_match[0]['_get_weather_'].id == "get_weather", "Function wasn't properly retrieved")
        self.assertTrue(my_match[1]['_get_weather_'].id == "print")

        my_match2 = find_matches("_var_._method_()")
        self.assertTrue(len(my_match2) == 1, "couldn't find attr func access")

        my_match3 = find_matches("weather._method_()")
        self.assertTrue(len(my_match3) == 1, "couldn't find attr func access")

        my_match4 = find_matches("_var_.get_weather()")
        self.assertTrue(len(my_match4) == 1, "couldn't find attr func access")

        MAIN_REPORT.clear()
        contextualize_report('book = {"number_of_pages":285, "price":99.23, "discount":0.1}\n'
                             'print(["price"])')
        parse_program()
        match = find_match("_var_([__str1__])")
        self.assertTrue(match["_var_"].id == "print", "couldn't find attr func access")

        contextualize_report('print("fun")')
        parse_program()
        matches = find_matches("_var_")
        var = matches[0]["_var_"]
        self.assertTrue(var.ast_name == "Name", "is: '{}' instead of Name".format(var.ast_name))

    def test_class_Names(self):
        contextualize_report("class myClass:\n"
                             "    def f(self):\n"
                             "        return 'hello world'")
        parse_program()
        matches = find_matches("class myClass:\n\tpass")
        matches_wildcard = find_matches("class _name_:\n\tpass")

        self.assertTrue(len(matches) == 1, "exact class name matching not working")
        self.assertTrue(len(matches_wildcard) == 1, "wild card class name matching not working")
        # Added functionality for matching class names
        var = matches_wildcard[0]["_name_"]
        self.assertTrue(var.id == "myClass", "is: '{}' instead of Name".format(var.id))

    def test_attribute_names(self):
        contextualize_report("import weather\n"
                             "weather_reports = get_weather('Data')\n"
                             "weather_reports = weather.get_weather['Data']\n"
                             "total = 0\n"
                             "for weather in weather_reports:\n"
                             "    total = total + weather\n"
                             "print(total)")

        my_match1 = find_matches("_var_._attr_[__str__]")
        self.assertTrue(len(my_match1) == 1, "couldn't find attr func access")

        self.assertTrue(my_match1[0]['_attr_'].id == "get_weather", "'{}' instead of 'get_weather'".format(
            my_match1[0]['_attr_'].id))

        my_match2 = find_matches("_var_.___[__str__]")
        self.assertTrue(len(my_match2) == 1, "couldn't wild card attribute access")

    def test_broken_traversal(self):
        contextualize_report("user entered gobblydegook")
        verify()
        parse = parse_program()
        self.assertFalse(parse.find_all('For'))

    def test_aug_assignment(self):
        contextualize_report(
            "magnitudes = [1.5, 1.9, 4.3, 2.1, 2.0, 3.6, 0.5, 2.5, 1.9, 4.0, 3.8, 0.7, 2.2, 5.1, 1.6]\n"
            "count = 0\n"
            "for item in magnitudes:\n"
            "    if item > 2.0:\n"
            "        count = count + 1\n"
            "print(count)")
        match = find_matches("for ___ in ___:\n"
                             "    __exp__\n"
                             "print(_var_)")[0]
        self.assertTrue(match["__exp__"].find_matches(match["_var_"].id))

        contextualize_report(
            "magnitudes = [1.5, 1.9, 4.3, 2.1, 2.0, 3.6, 0.5, 2.5, 1.9, 4.0, 3.8, 0.7, 2.2, 5.1, 1.6]\n"
            "count = 0\n"
            "for item in magnitudes:\n"
            "    if item > 2.0:\n"
            "        count += 1\n"
            "print(count)")
        match = find_matches("for ___ in ___:\n"
                             "    __exp__\n"
                             "print(_var_)")[0]
        m__exp__ = match["__exp__"]
        submatches = m__exp__.find_matches(match["_var_"].id, check_meta=False)
        self.assertTrue(submatches)

    def test_function_recursion(self):
        contextualize_report("def recursive(item):\n"
                             "    if item < 0:\n"
                             "        return 0\n"
                             "    else:"
                             "        return recursive(item - 1)")
        matches = find_matches("def _recur_(_var_):\n"
                               "    __exp__")
        for match in matches:
            __exp__ = match["__exp__"]
            _recur_ = match["_recur_"]
            _var_ = match["_var_"]
            self.assertTrue(__exp__.find_matches("{func}()".format(func=_recur_.id)),
                            "couldn't find recursive function call")

    def test_use_previous(self):
        contextualize_report('for reports in weather_reports:\n'
                             '    if report["Station"]["City"] == "Chicago":\n'
                             '        trend.append(reports["Data"]["Precipitation"])')
        matches = find_matches("for _var_ in ___:\n"
                               "    if __expr__ == __str2__:\n"
                               "        pass")
        for match in matches:
            __expr__ = match["__expr__"]
            submatch = __expr__.find_matches("_var2_[__expr__]")
            self.assertTrue(submatch)

        contextualize_report('for reports in weather_reports:\n'
                             '    if report["Station"]["City"] == "Chicago":\n'
                             '        trend.append(reports["Data"]["Precipitation"])')
        matches = find_matches("for _var_ in ___:\n"
                               "    if __expr__ == __str2__:\n"
                               "        pass")
        for match in matches:
            __expr__ = match["__expr__"]
            submatch = __expr__.find_matches("_var_[__expr__]", use_previous=True)
            self.assertFalse(submatch)

        contextualize_report('for reports in weather_reports:\n'
                             '    if report["Station"]["City"] == "Chicago":\n'
                             '        trend.append(reports["Data"]["Precipitation"])')
        matches = find_matches("for _var_ in ___:\n"
                               "    if __expr__ == __str2__:\n"
                               "        pass")
        for match in matches:
            __expr__ = match["__expr__"]
            submatch = __expr__.find_matches("_var_[__expr__]")
            self.assertFalse(submatch)

        contextualize_report("for item in item_list:\n"
                             "    if item < 0:\n"
                             "        n = n + item")
        matches = find_matches("for _var_ in ___:\n"
                               "    __expr__")
        for match in matches:
            __expr__ = match["__expr__"]
            submatch = __expr__.find_matches("_sum_ = _sum_ + _var_", use_previous=True)
            self.assertTrue(submatch)

    def test_match_root(self):
        contextualize_report("for item in item_list:\n"
                             "    if item < 0:\n"
                             "        n = n + item\n"
                             "n = 0")
        match01 = find_match("for ___ in ___:\n"
                             "    __expr__")
        match02 = find_match("_var_ = 0")
        match03 = find_match("_var_ = _var_ + _item_")
        root01 = match01.match_root.tree_id
        root02 = match02.match_root.tree_id
        root03 = match03.match_root.tree_id
        self.assertTrue(root01 < root02)
        self.assertTrue(root01 < root03)

    def test_copy(self):
        contextualize_report("for item in item_list:\n"
                             "    if item < 0:\n"
                             "        n = n + item\n"
                             "        i = i + 1\n"
                             "n = 0")
        match01 = find_match("for _item_ in ___:\n"
                             "    __expr__")
        map_size01 = len(match01.mappings.keys())

        match02 = find_match("___ = _item_ + 1", use_previous=match01)
        map_size02 = len(match01.mappings.keys())

        match03 = find_match("___ = _item_ + ___", use_previous=match01)
        map_size03 = len(match01.mappings.keys())
        map_size03_2 = len(match03.mappings.keys())

        match04 = find_match("___ = _item_ + 1")
        match05 = find_match("___ = _item_ + ___")
        map_size05 = len(match05.mappings.keys())

        self.assertTrue(map_size01 == map_size02 == map_size03)
        self.assertNotEqual(map_size03, map_size03_2)
        self.assertNotEqual(map_size03_2, map_size05)

        self.assertFalse(match02)
        self.assertTrue(match03)
        self.assertTrue(match04)

    def test_cait_get_match_names(self):
        contextualize_report("for item in item_list:\n"
                             "    if item < 0:\n"
                             "        n = n + item\n"
                             "        i = i + 1\n"
                             "n = 0")
        match = find_match("___ = _item_ + 1")
        self.assertEqual(match.names(), {'_item_': 'i'})

    def test_find_matches_expr2(self):
        contextualize_report('for prop_report in crime_reports:\n'
                             '    total_prop= total_prop + prop_report["Property Crime"]\n'
                             '    count_prop= count_prop +1\n'
                             'average_property = total_prop/count_prop\n'
                             'for violent_report in crime_reports:\n'
                             '    total_viol= total_viol + violent_report["Violent Crime"]\n'
                             '    count_viol= count_viol +1\n'
                             'average_violent= total_viol/count_viol\n')
        matches = find_matches("for ___ in __exp__:\n"
                               "    pass")
        self.assertEqual(4, len(matches))
        # TODO: This is 4 because right now pass matches to statements instead of an entire body


if __name__ == '__main__':
    unittest.main(buffer=False)

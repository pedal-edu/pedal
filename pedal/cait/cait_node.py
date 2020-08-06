"""
Module for the CaitNode class, which wraps AST nodes.
"""
import ast
from pedal.cait.ast_helpers import dump
from types import MethodType

from pedal.core.location import Location
from pedal.core.report import MAIN_REPORT


class CaitNode:
    """
    A wrapper class for AST nodes. Linearizes access to the children of the ast
    node and saves the field this AST node originated from.

    Attributes:
        ast_node (ast.AST): The original AstNode.

    TODO: May want to just add fields and methods to the existing AST nodes and
    use a production pattern instead.
    """

    def __init__(self, ast_node, my_field='', tid=0, lin_tree=None,
                 ancestor=None, report=None):
        """

        Args:
            ast_node (ast_node): The AST node to be wrapped
            my_field (str): the field of the parent node that produced this child.
            tid (int): the tree id
            lin_tree list of cait_node: A linear version of the tree
            ancestor (cait_node): The parent of this node
            report: The report associated with this particular match.
        """
        if report is None:
            report = MAIN_REPORT
        self.report = report
        self.children = []
        self.astNode = ast_node
        self.field = my_field
        self.tree_id = tid
        self.parent = ancestor
        if lin_tree is None:
            self.linear_tree = [self]
        else:
            lin_tree.append(self)
            self.linear_tree = lin_tree

        # reference to the easy node wrapping the ast_node
        setattr(ast_node, 'cait_node', self)

        tid_count = tid

        my_field_generator = ast.iter_fields(self.astNode)
        for item in my_field_generator:
            field, value = item
            # if the field doesn't have a value, no child exists
            if value is None:
                continue

            # If the children are not in an array, wrap it in an array for
            # consistency in the code the follows
            if not isinstance(value, list):
                value = [value]

            # Reference ast_node_visitor.js for the original behavior and keep note of it for the purposes of handling
            # the children noting the special case when the nodes of the array are actually parameters of the node
            # (e.g. a load function) instead of a child node
            for sub_value in value:
                if isinstance(sub_value, ast.AST):
                    new_child = CaitNode(sub_value, my_field=field,
                                         tid=tid_count + 1,
                                         lin_tree=self.linear_tree,
                                         ancestor=self,
                                         report=self.report)
                    self.children.append(new_child)
                    tid_count = len(self.linear_tree) - 1

    def __str__(self):
        return ''.join([self.field, "\n", dump(self.astNode)])

    def numeric_logic_check(self, mag, expr):
        """
        If this node is a Compare or BoolOp node, sees if the logic in expr (a javascript string being a logical
        statement) matches the logic of self. This assumes that we are only comparing numerical values to a single
        variable
        TODO: modify this to take multiple variables
        TODO: modify to support more than +, -, *, and / BinOps
        TODO: modify to support unary operators other than USub and Not
        TODO: This is very finicky and buggy, try not to use it
        Args:
            mag (float): the order of magnitude that should be added to numbers to check logic, 1 is usually a good value,
                    especially when working with the set of integers.
            expr (Compare or BoolOp): the "Compare" or "BoolOp" tree to check self against

        Returns:
            bool: True if self (typically student node) and expr are equivalent boolean expressions
        """

        def eval_unop(unop_num, unop_node):
            """

            Args:
                unop_num:
                unop_node:

            Returns:

            """
            operand = eval_selector(unop_num, unop_node.operand)
            op = unop_node.op_name

            return {"USub": -operand,
                    "Not": not operand}[op]

        def eval_binop(binop_num, binop_node):
            """

            Args:
                binop_num:
                binop_node:

            Returns:

            """
            left = eval_selector(binop_num, binop_node.left)
            right = eval_selector(binop_num, binop_node.right)
            op = binop_node.op_name

            return {
                "Add": left + right,
                "Sub": left - right,
                "Mult": left * right,
                "Div": left / right}[op]

        def eval_selector(op_num, op_expr):
            """

            Args:
                op_num:
                op_expr:

            Returns:

            """
            op_expr = op_num if op_expr.ast_name == "Name" else op_expr
            if isinstance(op_expr, (int, float)):
                return op_expr
            if op_expr.ast_name == "BinOp":
                return eval_binop(op_num, op_expr)
            if op_expr.ast_name == "UnaryOp":
                return eval_unop(op_num, op_expr)
            if op_expr.ast_name == "Num":
                return op_expr.n
            if op_expr.ast_name == "Constant":
                return op_expr.value
            raise NotImplementedError

        def eval_bool_comp(num_list, comp_ast):
            """

            Args:
                num_list:
                comp_ast:

            Returns:

            """
            ops = comp_ast.ops_names
            comps = comp_ast.comparators
            results = []
            current = comp_ast.left
            left = current

            for num_i in num_list:
                result = True
                for op, comp in zip(ops, comps):
                    current = eval_selector(num_i, current)
                    comp_p = eval_selector(num_i, comp)

                    res = {
                        "Eq": current == comp_p,
                        "NotEq": current != comp_p,
                        "Lt": current < comp_p,
                        "LtE": current <= comp_p,
                        "Gt": current > comp_p,
                        "GtE": current >= comp_p,
                    }[op]
                    current = comp
                    result = result and res
                    if not result:
                        break
                results.append(result)
                current = left
            return results

        def eval_boolop(num_list, boolop_ast):
            """

            Args:
                num_list:
                boolop_ast:

            Returns:

            """
            boolop = boolop_ast.op_name
            values = boolop_ast.values
            results_c = None
            is_and = boolop == "And"
            for value in values:
                if value.ast_name == "Compare":
                    results = eval_bool_comp(num_list, value)
                else:  # should be boolop
                    results = eval_boolop(num_list, value)
                if results_c is None:
                    results_c = results
                else:  # compile results
                    new_result = []
                    for result1, result2 in zip(results_c, results):
                        if is_and:
                            new_result.append(result1 and result2)
                        else:
                            new_result.append(result1 or result2)
                    results_c = new_result
            return results_c

        try:
            ins_expr = CaitNode(ast.parse(expr), report=self.report).body[0].value
            ins_nums = ins_expr.find_all(["Num", "Constant"])
            std_nums = self.find_all(["Num", "Constant"])
            test_nums = []
            for num in ins_nums:
                if hasattr(num, "n"):
                    raw_num = num.n
                else:
                    raw_num = num.value
                test_nums.append(raw_num)
                test_nums.append(raw_num + mag)
                test_nums.append(raw_num - mag)
            for num in std_nums:
                if hasattr(num, "n"):
                    raw_num = num.n
                else:
                    raw_num = num.value
                test_nums.append(raw_num)
                test_nums.append(raw_num + mag)
                test_nums.append(raw_num - mag)

            if self.ast_name == "Compare":
                std_res = eval_bool_comp(test_nums, self)
            elif self.ast_name == "BoolOp":
                std_res = eval_boolop(test_nums, self)
            else:
                return False

            if ins_expr.ast_name == "Compare":
                ins_res = eval_bool_comp(test_nums, ins_expr)
            elif ins_expr.ast_name == "BoolOp":
                ins_res = eval_boolop(test_nums, ins_expr)
            else:
                raise TypeError
            return ins_res == std_res
        except Exception:
            return False

    def get_next_tree(self):
        """Gets the next tree in the AST
        This method gets the next AST node that is of equal or higher level than self. Returns None if the end of the
        tree is reached
        TODO: Create a get sibling method.

        Returns:
            cait_node: The next tree in the AST

        """

        # adding function to track tree ids
        def visit_counter(self, node):
            """

            Args:
                self:
                node:
            """
            self.counter += 1
            self.generic_visit(node)

        node_counter = ast.NodeVisitor()
        setattr(node_counter, 'counter', self.tree_id)
        node_counter.visit = MethodType(visit_counter, node_counter)

        # getting ids
        node_counter.visit(self.astNode)
        out_of_tree = node_counter.counter >= len(self.linear_tree)  # check if out of bounds
        # len(self.children) > 0 and self.children[-1] == node_counter
        if out_of_tree:
            return None
        return self.linear_tree[node_counter.counter]

    def get_child(self, node):
        """

        Args:
            node: a non-CaitNode ast node

        Returns:
            cait_node: the corresponding cait_node to the child
        """
        if isinstance(node, ast.AST):
            for child in self.children:
                if child.astNode == node:
                    return child
        elif isinstance(node, int):
            return self.children(node)
        return None

    @staticmethod
    def get_ast_name(node):
        """

        Args:
            node:

        Returns:

        """
        return type(node).__name__

    def get_clashing_attr(self, key):
        """

        Args:
            key:

        Returns:

        """
        if key == "value":
            return self.get_value()

    def __getattr__(self, item):
        key = item
        """
        Non-ast node attributes based on ast_node attributes
        """
        node_name = CaitNode.get_ast_name(self.astNode)
        if node_name == "Assign" and key == "target":
            key = "targets"
        if item in AST_SINGLE_FUNCTIONS:
            key = item[:-5]  # strip suffix '_name'
        if item in AST_ARRAYS_OF_FUNCTIONS:
            key = item[:-6]  # strip suffix '_names'

        """
        Non-ast node attributes
        """
        if key == 'next_tree':
            return self.get_next_tree()
        if key == 'ast_name':
            return node_name
        elif key == '_name':
            return self.astNode.name
        elif key == 'ast_node':
            return self.astNode
        else:  # ast node attributes or derivative attributes
            if hasattr(self.astNode, key):
                # noinspection PyBroadException
                try:
                    field = self.astNode.__getattribute__(key)
                except Exception:
                    field = None
                if node_name == "Assign" and item != key:
                    if item == "target":
                        return field[0].cait_node  # Get's the relevant ast node
                    elif item == "targets" and isinstance(field, list):
                        easy_array = []
                        for node in field:
                            easy_array.append(node.cait_node)
                        return easy_array
                    else:
                        return field
                elif item in AST_SINGLE_FUNCTIONS:
                    return type(field).__name__
                elif item in AST_ARRAYS_OF_FUNCTIONS:
                    str_ops_list = []
                    for op in field:
                        str_ops_list.append(type(op).__name__)
                        return str_ops_list
                elif isinstance(field, ast.AST):
                    return field.cait_node
                elif isinstance(field, list):
                    try:
                        return [f.cait_node for f in field]
                    except AttributeError:
                        # This can only happen in NonLocals, which has a list
                        # of raw strings in the `names` property
                        return field
                else:
                    return field
            else:  # get added field that may have existed for different node types
                return self.get_clashing_attr(key)

    def find_matches(self, pattern, is_mod=False, check_meta=True, use_previous=True):
        """
        Retrieves any patterns that match against this CaitNode. Expected to be
        used for subpattern matching.
        Args:
            pattern (CaitNode/str): The pattern searched for in this cait_node
            is_mod (bool): Assumes that this node is a module node
            check_meta (bool): Checks if meta information of the nodes also matches (e.g. instead of just checking children,
                            also checking whether the children have the same field name in both the pattern and the
                            source
            use_previous (bool): If True, the match will be searched while inheriting the symbol table of the parent. This
                            means that variable consistency must be maintained between parent and child matches.

        Returns:
            :obj: 'list' of :'obj': AstMap: a list of matches

        """
        # Avoid circular import
        import pedal.cait.stretchy_tree_matching as stm
        is_node = isinstance(pattern, CaitNode)
        if not isinstance(pattern, str) and not is_node:
            raise TypeError("pattern expected str or CaitNode, found {0}".format(type(pattern)))
        matcher = stm.StretchyTreeMatcher(pattern, report=self.report)
        if (not is_node and not is_mod) and len(matcher.root_node.children) != 1:
            raise ValueError("pattern does not evaluate to a singular statement")
        use_previous = self.map if use_previous else None
        return matcher.find_matches(self, check_meta=check_meta, use_previous=use_previous)

    def find_match(self, pattern, is_mod=False, check_meta=True, use_previous=True):
        """

        Args:
            pattern:
            is_mod:
            check_meta:
            use_previous:

        Returns:

        """
        matches = self.find_matches(pattern, is_mod, check_meta=check_meta, use_previous=use_previous)
        if len(matches) != 0:
            return matches[0]
        return None

    def find_all(self, node_type):
        """Finds all nodes defined by string node_type

        Args:
            node_type: the string representing the "type" of node to look for

        Returns:
            a list of Ast Nodes (cait_nodes) of self that are of the specified type (including self if self
                    meets that criteria)
        """
        items = []
        visitor = ast.NodeVisitor()
        setattr(visitor, "items", items)

        def main_visit(self, node):
            """

            Args:
                self:
                node:

            Returns:

            """
            self.items.append(node.cait_node)
            return self.generic_visit(node)

        if type(node_type) is not list:
            node_type_list = [node_type]
        else:
            node_type_list = node_type

        for node_t in node_type_list:
            func_name = 'visit_' + node_t
            func_ref = main_visit
            setattr(visitor, func_name, MethodType(func_ref, visitor))

        visitor.visit(self.astNode)
        return visitor.items

    def has(self, node):
        """
        Determine if this node has the given `node`. Specifically, it checks if the ast has a given Constant or variable
        This method does NOT check for equality of two asts. Use find_matches for that functionality
        Args:
            node (): A constant (int, float, str), or Name astnode

        Returns: True if found, False otherwise

        """
        if isinstance(node, (int, float, str)):
            visitor = ast.NodeVisitor()
            has_constant = []

            def visit_Constant(self, potential):
                has_constant.append(node == potential.value)
                return self.generic_visit(potential)

            def visit_Num(self, potential):
                has_constant.append(node == potential.n)
                return self.generic_visit(potential)

            def visit_Str(self, potential):
                has_constant.append(node == potential.s)
                return self.generic_visit(potential)

            visitor.visit_Num = MethodType(visit_Num, visitor)
            visitor.visit_Constant = MethodType(visit_Constant, visitor)
            visitor.visit_Str = MethodType(visit_Str, visitor)
            visitor.visit(self.astNode)
            return any(has_constant)
        elif node.ast_name != "Name":
            return False
        visitor = ast.NodeVisitor()
        has_name = []

        def visit_Name(self, potential):
            """

            Args:
                self:
                potential:

            Returns:

            """
            has_name.append(node.id == potential.id)
            return self.generic_visit(potential)

        visitor.visit_Name = MethodType(visit_Name, visitor)
        visitor.visit(self.astNode)
        return any(has_name)

    def is_before(self, other):
        """
        Uses tree id to check if self node came before other.
        Args:
            other (cait_node): the other node to compare to

        Returns:
            bool: True if self is before other
        """
        try:
            return self.tree_id < other.tree_id and self.linear_tree == other.linear_tree
        except Exception:
            raise TypeError

    def is_ast(self, ast_name):
        """
        Checks self is the type of the specified ast node
        Args:
            ast_name (str): The name of the ast node type

        Returns:
            bool: True if this node's ast name matches the specified one
        """
        # TODO: Deal with this compatibility issue in a more elegant way
        if not isinstance(ast_name, str):
            ast_name = CaitNode.get_ast_name(ast_name.astNode)
        self_name = CaitNode.get_ast_name(self.astNode).lower()
        other_name = ast_name.lower()
        evaluation = self_name == other_name
        if self_name == "constant" and other_name in ["num", "str", "bytes"]:
            if other_name == "num" and type(self.n) in [float, int]:
                evaluation = True
            elif other_name == "str" and type(self.s) is str:
                evaluation = True
            elif other_name == "bytes" and type(self.s) is bytes:
                evaluation = True
        return evaluation

    def is_method(self):
        """
        Checks if self is a method

        Returns:
            bool: True if I'm a FunctionDef, and if any of my parents are ClassDef.
        """
        # Check if I'm a FunctionDef, and if any of my parents are ClassDef.
        if self.ast_name != "FunctionDef":
            return False
        current = self.parent
        while current is not None:
            if current.ast_name == "ClassDef":
                return True
            # Don't treat closures as methods
            elif current.ast_name == "FunctionDef":
                return False
            current = current.parent
        return False

    def get_data_state(self):
        """
        Gets the data_state object of self

        Returns:
            data_state or None: returns data_state if self is a name and exists, otherwise None
        """
        if self.ast_name != "Name":
            return None
        try:
            return self.report['tifa']['latest'].top_level_variables[self.id]
        except KeyError:
            return None

    def get_data_type(self):
        """

        Returns:
            type of the variable associated with this node if it's a name node, otherwise None.
        """
        state = self.get_data_state()
        if state is None:
            return None
        else:
            return state.type

    def was_type(self, tp):
        """

         Returns:
             type of the variable associated with this node if it's a name node, otherwise None.
         """
        state = self.get_data_state()
        if state is None:
            return None
        else:
            return state.was_type(tp)

    def get_value(self):
        """"
        Returns:
            Value of node if Num or Str, and get_data_state if Name
        """
        value = None
        if self.is_ast("Num"):
            value = self.n
        elif self.is_ast("Str"):
            value = self.s
        elif self.is_ast("Constant"):
            value = self.value
        elif self.is_ast("Name"):
            # TODO: Decide on what this should return...
            value = self.id
        return value

    def locate(self):
        """
        Returns:
            pedal.core.Location: The location of this node.
        """
        return Location(self.astNode.lineno, col=self.astNode.col_offset)


AST_SINGLE_FUNCTIONS = ["ctx_name", "op_name"]
AST_ARRAYS_OF_FUNCTIONS = ["ops_names"]

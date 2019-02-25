import ast
import re
from pedal.cait.ast_map import AstMap
from pedal.cait.cait_node import CaitNode

# "Enums" for _name_regex
_VAR = "var"
_EXP = "exp"
_WILD = "wild"


def is_primitive(item):
    """
    Determines if the given item is a primitive value (either an int, float,
    str, bool, or None).

    Args:
        item (any): Any value
    Returns:
        bool: Whether the item is a primitive value.
    """
    return isinstance(item, (int, float, str, bool)) or item is None


def _name_regex(name_id):
    var_match = re.compile('^_[^_].*_$')  # /regex
    exp_match = re.compile('^__.*__$')  # /regex
    wild_card = re.compile('^___$')  # /regex
    return {_VAR: var_match.match(name_id),
            _EXP: exp_match.match(name_id),
            _WILD: wild_card.match(name_id)}


class StretchyTreeMatcher:
    def __init__(self, ast_or_code, report, filename="__main__"):
        """
        The StretchyTreeMatcher is used to compare a pattern against some
        student code. It produces a set of potential mappings between them.

        Args:
            ast_or_code (str or AstNode): The students' code or a valid AstNode from
                `ast.parse`. If the code has invalid syntax, a SyntaxError
                will be raised.
            filename (str): The filename to parse with - only used for error
                reporting.
            report (Report): A report to obtain data from.
        """
        self.report = report
        if isinstance(ast_or_code, str):
            ast_node = ast.parse(ast_or_code, filename)
        else:
            ast_node = ast_or_code
        # Build up root
        if ast_node is None:
            self.root_node = None
        elif isinstance(ast_node, CaitNode):
            self.root_node = ast_node
        else:
            self.root_node = CaitNode(ast_node, "none", report=self.report)

    def find_matches(self, ast_or_code, filename="__main__", check_meta=True):
        """
        Args:
            ast_or_code (str or AstNode): The students' code or a valid AstNode from
                `ast.parse`. If the code has invalid syntax, a SyntaxError
                will be raised.
            filename (str): The filename to parse with - only used for error
                reporting.
            check_meta (bool): Determine if the nodes came from the same AST
                field.
        Returns:
            list[AstMap]: A list of AstMaps that are suitable matches.
        """
        if isinstance(ast_or_code, str):
            other_tree = CaitNode(ast.parse(ast_or_code, filename), report=self.report)
        elif isinstance(ast_or_code, CaitNode):
            other_tree = ast_or_code
        else:
            other_tree = CaitNode(ast_or_code, "none", report=self.report)
        explore_root = self.root_node
        if self.root_node is not None:
            while (len(explore_root.children) == 1 and
                   explore_root.ast_name in ["Expr", "Module"]):
                explore_root = explore_root.children[0]
                explore_root.field = "none"
        return self.any_node_match(explore_root, other_tree,
                                   check_meta=check_meta)

    def any_node_match(self, ins_node, std_node, check_meta=True, cut=False):
        """
        Finds whether ins_node can be matched to some node in the tree std_node

        Args:
            ins_node:
            std_node:
            check_meta:
            cut:

        Returns:
            list of AstMaps: a mapping of nodes and a symbol table mapping ins_node to
                some node in the tree std_node or False if such a matching does not
                exist
        """
        # @TODO: create a more public function that converts ins_node and std_node into CaitNodes
        # TODO: Create exhaustive any_node_match
        # matching: an object representing the mapping and the symbol table
        matching = self.deep_find_match(ins_node, std_node, check_meta)
        # if a direct matching is found
        if matching:
            for match in matching:
                match.match_root = std_node
        else:
            matching = []
        #    return matching  # return it
        # if not matching or exhaust:  # otherwise
        # try to matching ins_node to each child of std_node, recursively
        for std_child in std_node.children:
            matching_c = self.any_node_match(ins_node, std_child, check_meta=check_meta, cut=cut)
            if matching_c:
                for match in matching_c:
                    match.match_root = std_child
                # return matching
                matching = matching + matching_c
        if len(matching) > 0:
            return matching
        return []

    def deep_find_match(self, ins_node, std_node, check_meta=True):
        """
        Finds whether ins_node and matches std_node and whether ins_node's children flexibly match std_node's children
        in order
        Args:
            ins_node: The instructor ast that should be included in the student AST
            std_node: The student AST that we are searching for the included tree
            check_meta: Flag, if True, check whether the two nodes originated from the same ast field

        Returns:
            a mapping of nodes and a symbol table mapping ins_node to std_node, or [] if no mapping was found
        """
        method_name = "deep_find_match_" + type(ins_node.astNode).__name__
        target_func = getattr(self, method_name, self.deep_find_match_generic)
        return target_func(ins_node, std_node, check_meta)

    # noinspection PyPep8Naming
    def deep_find_match_Name(self, ins_node, std_node, check_meta=True):
        name_id = ins_node.astNode.id
        match = _name_regex(name_id)
        mapping = AstMap()
        matched = False
        meta_matched = self.metas_match(ins_node, std_node, check_meta)
        if match[_VAR] and meta_matched:  # if variable
            # This if body is probably unnecessary.
            if type(std_node.astNode).__name__ == "Name":
                return self.deep_find_match_generic(ins_node, std_node, check_meta)
        # could else return False, but shallow_match_generic should do this as well
        elif match[_EXP]:  # and meta_matched:  # if expression
            # terminate recursion, the whole subtree should match since expression nodes match to anything
            mapping.add_exp_to_sym_table(ins_node, std_node)
            matched = True
        elif match[_WILD] and meta_matched:  # if wild card, don't care
            # terminate the recursion, the whole subtree should match since wild cards match to anything
            matched = True

        if matched:
            mapping.add_node_pairing(ins_node, std_node)
            return [mapping]
        # else
        return self.deep_find_match_generic(ins_node, std_node, check_meta)

    # noinspection PyPep8Naming
    def deep_find_match_BinOp(self, ins_node, std_node, check_meta=True):
        op = ins_node.astNode.op
        op = type(op).__name__
        is_generic = not (op == "Mult" or op == "Add")
        if is_generic:
            return self.deep_find_match_generic(ins_node, std_node, check_meta)
        else:  # this means that the node is clearly commutative
            return self.deep_find_match_binflex(ins_node, std_node, False)

    # noinspection PyMethodMayBeStatic
    def binflex_helper(self, case_left, case_right, new_mappings, base_mappings):
        """
        adds to new_mappings (return/modify by argument) the mappings for both the left and right subtrees as denoted by
        case_left and case_right
        Args:
            case_left: The mappings for the left opperand
            case_right: The mappings for the right opperand
            new_mappings: The new set of mappings to generate
            base_mappings: The original mappings of the binop node

        Returns:
            None
        """
        if case_left and case_right:
            for case_l in case_left:
                new_map = base_mappings[0].new_merged_map(case_l)
                for case_r in case_right:
                    both = new_map.new_merged_map(case_r)
                    if not both.has_conflicts():
                        new_mappings.append(both)

    def deep_find_match_binflex(self, ins_node, std_node, check_meta=False):
        base_mappings = self.shallow_match(ins_node, std_node, check_meta)
        if not base_mappings:
            return []
        op_mappings = self.shallow_match(ins_node.children[1], std_node.children[1], check_meta=True)
        if not op_mappings:
            return []
        base_mappings = [base_mappings[0].new_merged_map(op_mappings[0])]

        if base_mappings:
            ins_left = ins_node.children[0]  # instructor left ast node
            ins_right = ins_node.children[2]  # instructor right ast node
            std_left = std_node.children[0]  # student left ast node
            std_right = std_node.children[2]  # student right ast node
            new_mappings = []
            # case 1: ins_left->std_left and ins_right->std_right
            case_left = self.deep_find_match(ins_left, std_left, False)
            case_right = self.deep_find_match(ins_right, std_right, False)
            self.binflex_helper(case_left, case_right, new_mappings, base_mappings)
            # case 2: ins_left->std_right and ins_right->std_left
            case_left = self.deep_find_match(ins_left, std_right, False)
            case_right = self.deep_find_match(ins_right, std_left, False)
            self.binflex_helper(case_left, case_right, new_mappings, base_mappings)
            if len(new_mappings) == 0:
                return []
            return new_mappings
        return []

    def deep_find_match_Expr(self, ins_node, std_node, check_meta=True):
        """
        An Expression node (not to be confused with expressions denoted by the instructor nodes in Name ast nodes)
        checks whether it should be generic, or not
        Args:
            ins_node: Instructor ast to find in the student ast
            std_node: Student AST to search for the instructor ast in
            check_meta: flag to check whether the fields of the instructor node and the student node should match

        Returns:
            AstMap: a mapping between the instructor and student asts, or False if such a mapping doesn't exist
        """
        # if check_meta and ins_node.field != std_node.field:
        if not self.metas_match(ins_node, std_node, check_meta):
            return []
        mapping = AstMap()
        value = ins_node.value
        ast_type = type(value.astNode).__name__
        if ast_type == "Name":
            name_id = value.astNode.id
            exp_match = re.compile('^__.*__$')  # /regex
            wild_card = re.compile('^___$')  # /regex
            matched = False
            meta_matched = self.metas_match(ins_node, std_node, check_meta)
            if exp_match.match(name_id):  # and meta_matched:  # if expression
                # terminate recursion, the whole subtree should match since expression nodes match to anything
                mapping.add_exp_to_sym_table(value, std_node)
                matched = True
            elif wild_card.match(name_id) and meta_matched:  # if wild card, don't care
                # terminate the recursion, the whole subtree should match since wild cards match to anything
                matched = True
            if matched:
                mapping.add_node_pairing(ins_node, std_node)
                return [mapping]
        return self.deep_find_match_generic(ins_node, std_node, check_meta)

    def deep_find_match_generic(self, ins_node, std_node, check_meta=True):
        """
        This first uses shallow match to find a base map (match) from which to
        build off. The algorithm then tracks all the possible mappings that
        match a given child node in the instructor AST, keeping track of which
        siblings have been visited.

        For each instructor child, when all children of the student node have
        been iterated through recursively, a helper function is called. This
        helper function determines which possible children validly can extend
        the base match to create a set of new base maps through use of the
        indicies of the sibilings.

        The process repeats itself until no matches can be grown or until each
        instructor child node has been visited

        Args:
            ins_node: Instructor ast to find in the student ast
            std_node: Student AST to search for the instructor ast in
            check_meta: flag to check whether the fields of the instructor node and the student node should match

        Returns:
            a mapping between the isntructor and student asts, or [] if such a mapping doesn't exist
        """
        base_mappings = self.shallow_match(ins_node, std_node, check_meta)
        if base_mappings:
            # base case this runs 0 times because no children
            # find each child of ins_node that matches IN ORDER
            base_sibs = [-1]
            youngest_sib = 0
            # for each child
            for i, insChild in enumerate(ins_node.children):
                # make a new set of maps
                running_maps = []
                running_sibs = []
                # accumulate all potential matches for current child
                for j, std_child in enumerate(std_node.children[youngest_sib:], youngest_sib):
                    std_child = std_node.children[j]
                    new_mapping = self.deep_find_match(insChild, std_child, check_meta)
                    if new_mapping:
                        running_maps.append(new_mapping)
                        running_sibs.append(j)
                map_update = self.map_merge(base_mappings, base_sibs, running_maps, running_sibs)
                if map_update is None:
                    return []
                base_mappings = map_update['new_maps']
                base_sibs = map_update['new_sibs']
                youngest_sib = map_update['youngest_sib'] + 1
            return base_mappings
        return []

    # noinspection PyMethodMayBeStatic
    def map_merge(self, base_maps, base_sibs, run_maps, run_sibs):
        """
        Merges base_maps with the current possible maps. Helper method to deep_find_match_generic. checks whether each
        mapping in run_maps can extend the match to any possible mapping in base_maps.

        Args:
            base_maps: The original mappings
            base_sibs: The corresponding siblings for each mapping in base_maps
            run_maps: The set of maps to merge into the current base_maps
            run_sibs: The corresponding siblings for each mapping in run_maps

        Returns:
            A new set of maps for all valid extensions of base_maps with running maps
        """
        # no matching nodes were found
        if len(run_maps) == 0:
            return None
        new_maps = []
        new_sibs = []
        youngest_sib = run_sibs[0]
        for baseMap, base_sib in zip(base_maps, base_sibs):
            for run_map, runSib in zip(run_maps, run_sibs):
                if runSib > base_sib:
                    for run_mapsub in run_map:
                        new_map = baseMap.new_merged_map(run_mapsub)
                        if not new_map.has_conflicts():  # if it's a valid mapping
                            new_maps.append(new_map)
                            new_sibs.append(runSib)
        if len(new_maps) == 0:
            return None
        return {
            'new_maps': new_maps,
            'new_sibs': new_sibs,
            'youngest_sib': youngest_sib
        }

    # noinspection PyMethodMayBeStatic,PyPep8Naming,PyUnusedLocal
    def shallow_match_Module(self, ins_node, std_node, check_meta=True):
        """
        Flexibly matches a module node to a module or a body
        Args:
            ins_node:
            std_node:
            check_meta:

        Returns:
            a mapping of ins_node to std_node, or False if doesn't match
        """
        if type(std_node.astNode).__name__ == "Module" or std_node.field == "body":
            mapping = AstMap()
            mapping.add_node_pairing(ins_node, std_node)
            return [mapping]
        return []

    def shallow_symbol_handler(self, ins_node, std_node, id_val, check_meta=True):
        """
        TODO: Make this handle the func field to handle functions
        Matches ins_node to std_node for different cases of encountering a name node in ins_node
            case 1: _var_ matches if std_node is a name node and automatically returns a mapping and symbol table
            case 2: __exp__ matches to any subtree and automatically returns a mapping and symbol table
            case 3: ___ matches to any subtree and automatically returns a mapping
            case 4: matches only if the exact names are the same (falls through to shallow_match_generic)
        Args:
            ins_node:
            std_node:
            id_val:
            check_meta:

        Returns:
            list of AstMap: a mapping of ins_node to std_node and possibly a symbol_table, or False if it doesn't match
        """
        name_id = ins_node.astNode.__getattribute__(id_val)
        match = _name_regex(name_id)
        mapping = AstMap()
        matched = False
        # TODO: add functionality to add function references to func_table?
        meta_matched = self.metas_match(ins_node, std_node, check_meta)
        if match[_VAR] and meta_matched:  # variable
            if type(std_node.astNode).__name__ == "Name" or id_val == "attr":
                if id_val == "attr":
                    std_node.astNode.id = std_node.astNode.attr
                if std_node.field == "func" and ins_node.field != "none":
                    # TODO: This 'ins_node.field != "none"' code is for an obscure edge case where the instructor code
                    # is only _var_
                    mapping.add_func_to_sym_table(ins_node, std_node)
                else:
                    mapping.add_var_to_sym_table(ins_node, std_node)  # TODO: Capture result?
                matched = True
        # could else return False, but shallow_match_generic should do this as well
        elif match[_EXP] and meta_matched:  # expression TODO: In theory this won't run?
            mapping.add_exp_to_sym_table(ins_node, std_node)
            matched = True
        elif match[_WILD] and meta_matched:  # don't care TODO: In theory this won't run?
            matched = True

        if matched:
            mapping.add_node_pairing(ins_node, std_node)
            return [mapping]
        # else
        return self.shallow_match_generic(ins_node, std_node, check_meta)

    # noinspection PyPep8Naming,PyMethodMayBeStatic
    def shallow_func_handle(self, ins_node, std_node, check_meta=True):
        if ins_node.field == "func" and std_node.field == "func":
            ins_node.astNode.id = ins_node.astNode.attr
            return self.shallow_symbol_handler(ins_node, std_node, "attr", check_meta)
        return self.shallow_match_generic(ins_node, std_node, check_meta)

    def shallow_match_Attribute(self, ins_node, std_node, check_meta=True):
        if ins_node.field == "func" and std_node.ast_name == "Attribute":
            return self.shallow_func_handle(ins_node, std_node, check_meta)
        elif std_node.ast_name == "Attribute":
            ins_node.astNode.id = ins_node.attr  # TODO: Fix this hack more gracefully
            # add_var_to_sym_table in ast_map needs the id attribute to make the map
            return self.shallow_symbol_handler(ins_node, std_node, "attr", check_meta)
        else:
            return self.shallow_match_generic(ins_node, std_node, check_meta)

    # noinspection PyPep8Naming
    def shallow_match_Name(self, ins_node, std_node, check_meta=True):
        """
        TODO: Make this handle the func field to handle functions
        Matches ins_node to std_node for different cases of encountering a name node in ins_node
            case 1: _var_ matches if std_node is a name node and automatically returns a mapping and symbol table
            case 2: __exp__ matches to any subtree and automatically returns a mapping and symbol table
            case 3: ___ matches to any subtree and automatically returns a mapping
            case 4: matches only if the exact names are the same (falls through to shallow_match_generic)
        Args:
            ins_node:
            std_node:
            check_meta:

        Returns:
            list of AstMap: a mapping of ins_node to std_node and possibly a symbol_table, or False if it doesn't match
        """
        return self.shallow_symbol_handler(ins_node, std_node, "id", check_meta)

    # noinspection PyPep8Naming,PyMethodMayBeStatic
    def shallow_match_Pass(self, ins_node, std_node, check_meta=True):
        """
        An empty body should match to anything
        Args:
            ins_node: Instructor ast to find in the student ast
            std_node: Student AST to search for the instructor ast in
            check_meta: flag to check whether the fields of the instructor node and the student node should match

        Returns:
            list of AstMap: a mapping between the isntructor and student asts, or False if such a mapping doesn't exist
        """
        # if check_meta and ins_node.field != std_node.field:
        if not self.metas_match(ins_node, std_node, check_meta):
            return []
        mapping = AstMap()
        mapping.add_node_pairing(ins_node, std_node)
        return [mapping]

    # noinspection PyPep8Naming,PyMethodMayBeStatic
    def shallow_match_Expr(self, ins_node, std_node, check_meta=True):
        """
        An Expression node (not to be confused with expressions denoted by the instructor nodes in Name ast nodes)
        should match to anything
        Args:
            ins_node: Instructor ast to find in the student ast
            std_node: Instructor ast to find in the student ast
            check_meta: flag to check whether the fields of the instructor node and the student node should match

        Returns:
            a mapping between the instructor and student asts, or False if such a mapping doesn't exist
        """
        # if check_meta and ins_node.field != std_node.field:
        if not self.metas_match(ins_node, std_node, check_meta):
            return []
        mapping = AstMap()
        mapping.add_node_pairing(ins_node, std_node)
        return [mapping]

    def shallow_match_Call(self, ins_node, std_node, check_meta=True):
        return self.shallow_match_main(ins_node, std_node, check_meta, ignores=None)
        # matches = self.shallow_match_main(ins_node, std_node, check_meta, ignores=["func"])
        # if matches:
        #    pass
        # return None
        # TODO: Make this handle Calls more intelligently

    # noinspection PyPep8Naming
    def shallow_match_FunctionDef(self, ins_node, std_node, check_meta=True):
        ins = ins_node.astNode
        std = std_node.astNode
        meta_matched = self.metas_match(ins_node, std_node, check_meta)
        is_match = type(ins).__name__ == type(std).__name__ and meta_matched
        mapping = self.shallow_match_main(ins_node, std_node, check_meta, ignores=['name', 'args'])
        matched = False
        if is_match and mapping:
            name = ins.name
            match = _name_regex(name)
            if match[_VAR] and meta_matched:  # variable
                mapping[0].add_func_to_sym_table(ins_node, std_node)  # TODO: Capture result?
                matched = True
            elif match[_WILD] and meta_matched:
                matched = True
            elif name == std.name and meta_matched:
                matched = True
        if matched:
            return mapping
        else:
            return []

    # noinspection PyMethodMayBeStatic
    def shallow_match_generic(self, ins_node, std_node, check_meta=True):
        """
        Checks that all non astNode attributes are equal between ins_node and std_node
        Args:
            ins_node: Instructor ast root node
            std_node: Student AST root node
            check_meta: flag to check whether the fields of the instructor node and the student node should match

        Returns:
            list of AstMap: a mapping between the instructor and student root nodes (potentially empty)
        """
        return self.shallow_match_main(ins_node, std_node, check_meta)

    def shallow_match_main(self, ins_node, std_node, check_meta=True, ignores=None):
        """
        Checks that all non astNode attributes are equal between ins_node and std_node
        Args:
            ins_node: Instructor ast root node
            std_node: Student AST root node
            check_meta: flag to check whether the fields of the instructor node and the student node should match
            ignores: a mapping between the instructor and student root nodes, or False if such a mapping doesn't exist

        Returns:

        """
        if ignores is None:
            ignores = []
        ins = ins_node.astNode
        std = std_node.astNode
        ins_field_list = list(ast.iter_fields(ins))
        std_field_list = list(ast.iter_fields(std))
        meta_matched = self.metas_match(ins_node, std_node, check_meta)
        is_match = len(ins_field_list) == len(std_field_list) and type(ins).__name__ == type(
            std).__name__ and meta_matched
        for insTup, stdTup in zip(ins_field_list, std_field_list):
            if not is_match:
                break

            ins_field = insTup[0]
            ins_value = insTup[1]
            std_field = stdTup[0]
            std_value = stdTup[1]

            if ins_value is None:
                continue

            ignore_field = ins_field in ignores

            is_match = (ins_field == std_field) or ignore_field

            if not isinstance(ins_value, list):
                ins_value = [ins_value]

            if not isinstance(std_value, list):
                std_value = [std_value]

            # is_match = len(ins_value) == len(std_value)# for stretchy matching this isn't True
            # Reference ast_node_visitor.js for the original behavior and keep note of it for the purposes of handling
            # the children noting the special case when the nodes of the array are actually parameters of the node
            # (e.g. a load function) instead of a child node
            if not ignore_field:
                for inssub_value, stdsub_value in zip(ins_value, std_value):
                    if not is_match:
                        break
                    # TODO: make this a smarter comparison, maybe handle dictionaries, f-strings, tuples, etc.
                    if is_primitive(inssub_value):
                        is_match = inssub_value == stdsub_value
        if is_match:
            mapping = AstMap()  # return MAPPING
            mapping.add_node_pairing(ins_node, std_node)
            return [mapping]
        else:
            return []

    # filter function for various types of nodes
    def shallow_match(self, ins_node, std_node, check_meta=True):
        method_name = 'shallow_match_' + type(ins_node.astNode).__name__
        target_func = getattr(self, method_name, self.shallow_match_generic)
        return target_func(ins_node, std_node, check_meta)

    @staticmethod
    def metas_match(ins_node, std_node, check_meta=True):
        return (check_meta and ins_node.field == std_node.field) or not check_meta or ins_node.field == "none"

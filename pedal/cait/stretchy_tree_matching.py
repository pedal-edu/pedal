import ast
import re
from pedal.cait.ast_map import *
from pedal.cait.easy_node import *


def is_primitive(item):
    return isinstance(item, (int, float, str, bool)) or item is None


class StretchyTreeMatcher:
    def __init__(self, code, filename="__main__"):
        if isinstance(code, str):
            ast_node = ast.parse(code, filename)
        else:
            ast_node = code
        if ast_node is None:
            self.rootNode = None
        elif isinstance(ast_node, EasyNode):
            self.rootNode = ast_node
        else:
            self.rootNode = EasyNode(ast_node, "none")

    def find_matches(self, other, filename="__main__", check_meta=True, cut=False):
        # TODO: check that both are ast nodes at the module level
        if isinstance(other, str):
            other_tree = ast.parse(other, filename)
        else:
            other_tree = other
        if isinstance(other_tree, EasyNode):
            easy_other = other_tree
        else:
            easy_other = EasyNode(other_tree, "none")
        explore_root = self.rootNode
        if cut and (self.rootNode is not None):
            while len(explore_root.children) == 1:
                explore_root = explore_root.children[0]
                explore_root.field = "none"
        # return self.any_node_match(self.rootNode, easy_other, check_meta=check_meta)
        return self.any_node_match(explore_root, easy_other, check_meta=check_meta, cut=cut)

    '''
    Finds whether ins_node can be matched to some node in the tree std_node
    @return a mapping of nodes and a symbol table mapping ins_node to some node in the tree std_node or False if such a 
    matching does not exist
    '''

    def any_node_match(self, ins_node, std_node, check_meta=True, cut=False):
        # @TODO: create a more public function that converts ins_node and std_node into EasyNodes
        # TODO: Create exhaustive any_node_match
        # matching: an object representing the mapping and the symbol table
        matching = self.deep_find_match(ins_node, std_node, check_meta)
        # if a direct matching is found
        if matching:
            for match in matching:
                match.match_root = std_node
                if len(match.mappings.values) > 1:
                    match.match_lineno = match.mappings.values[1].lineno
                else:
                    match.match_lineno = match.mappings.values[0].lineno
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
                    if len(match.mappings.values) > 1:
                        match.match_lineno = match.mappings.values[1].lineno
                    else:
                        match.match_lineno = match.mappings.values[0].lineno
                # return matching
                matching = matching + matching_c
        if len(matching) > 0:
            return matching
        return False

    def deep_find_match(self, ins_node, std_node, check_meta=True):
        """
        Finds whether ins_node and matches std_node and whether ins_node's children flexibly match std_node's children
        in order
        :param ins_node: The instructor ast that should be included in the student AST
        :param std_node: The student AST that we are searching for the included tree
        :param check_meta: Flag, if True, check whether the two nodes originated from the same ast field
        :return: a mapping of nodes and a symbol table mapping ins_node to std_node, or False if no mapping was found
        """
        method_name = "deep_find_match_" + type(ins_node.astNode).__name__
        target_func = getattr(self, method_name, self.deep_find_match_generic)
        return target_func(ins_node, std_node, check_meta)

    # noinspection PyPep8Naming
    def deep_find_match_Name(self, ins_node, std_node, check_meta=True):
        name_id = ins_node.astNode.id
        var_match = re.compile('^_[^_].*_$')  # /regex
        exp_match = re.compile('^__.*__$')  # /regex
        wild_card = re.compile('^___$')  # /regex
        mapping = AstMap()
        matched = False
        meta_matched = self.metas_match(ins_node, std_node, check_meta)
        if var_match.match(name_id) and meta_matched:  # if variable
            # This if body is probably unnecessary.
            if type(std_node.astNode).__name__ == "Name":
                return self.deep_find_match_generic(ins_node, std_node, check_meta)
        # could else return False, but shallow_match_generic should do this as well
        elif exp_match.match(name_id):  # and meta_matched:  # if expression
            # terminate recursion, the whole subtree should match since expression nodes match to anything
            mapping.add_exp_to_sym_table(ins_node, std_node)
            matched = True
        elif wild_card.match(name_id) and meta_matched:  # if wild card, don't care
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
        :param case_left: The mappings for the left opperand
        :param case_right: The mappings for the right opperand
        :param new_mappings: The new set of mappings to generate
        :param base_mappings: The original mappings of the binop node
        """
        if case_left and case_right:
            for case_l in case_left:
                new_map = base_mappings[0].new_merged_map(case_l)
                for case_r in case_right:
                    both = new_map.new_merged_map(case_r)
                    new_mappings.append(both)

    def deep_find_match_binflex(self, ins_node, std_node, check_meta=False):
        base_mappings = self.shallow_match(ins_node, std_node, check_meta)
        if not base_mappings:
            return False
        op_mappings = self.shallow_match(ins_node.children[1], std_node.children[1], check_meta=True)
        if not op_mappings:
            return False
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
                return False
            return new_mappings
        return False

    def deep_find_match_Expr(self, ins_node, std_node, check_meta=True):
        """
        An Expression node (not to be confused with expressions denoted by the instructor nodes in Name ast nodes)
        checks whether it should be generic, or not
        :param ins_node: Instructor ast to find in the student ast
        :param std_node: Student AST to search for the instructor ast in
        :param check_meta: flag to check whether the fields of the instructor node and the student node should match
        :return: a mapping between the instructor and student asts, or False if such a mapping doesn't exist
        """
        # if check_meta and ins_node.field != std_node.field:
        if not self.metas_match(ins_node, std_node, check_meta):
            return False
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
        This first uses shallow match to find a base map (match) from which to build off. The algorithm then tracks
        all the possible mappings that match a given child node in the instructor AST, keeping track of which siblings
        have been visited.

        For each instructor child, when all children of the student node have been iterated through recursively, a
        helper function is called. This helper function determines which possible children validly can extend the base
        match to create a set of new base maps through use of the indicies of the sibilings.

        The process repeats itself until no matches can be grown or until each instructor child node has been visited

        :param ins_node: Instructor ast to find in the student ast
        :param std_node: Student AST to search for the instructor ast in
        :param check_meta: flag to check whether the fields of the instructor node and the student node should match
        :return: a mapping between the isntructor and student asts, or False if such a mapping doesn't exist
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
                    return False
                base_mappings = map_update['new_maps']
                base_sibs = map_update['new_sibs']
                youngest_sib = map_update['youngest_sib'] + 1
            return base_mappings
        return False

    # noinspection PyMethodMayBeStatic
    def map_merge(self, base_maps, base_sibs, run_maps, run_sibs):
        """
        Merges base_maps with the current possible maps. Helper method to deep_find_match_generic. checks whether each
        mapping in run_maps can extend the match to any possible mapping in base_maps.

        :param base_maps: The original mappings
        :param base_sibs: The corresponding siblings for each mapping in base_maps
        :param run_maps: The set of maps to merge into the current base_maps
        :param run_sibs: The corresponding siblings for each mapping in run_maps
        :return: A new set of maps for all valid extensions of base_maps with running maps
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
        map_update = None
        if len(new_maps) != 0:
            map_update = dict()
            map_update['new_maps'] = new_maps
            map_update['new_sibs'] = new_sibs
            map_update['youngest_sib'] = youngest_sib
        return map_update

    # noinspection PyMethodMayBeStatic,PyPep8Naming,PyUnusedLocal
    def shallow_match_Module(self, ins_node, std_node, check_meta=True):
        """
        Flexibly matches a module node to a module or a body
        :return: a mapping of ins_node to std_node, or False if doesn't match
        """
        if type(std_node.astNode).__name__ == "Module" or std_node.field == "body":
            mapping = AstMap()
            mapping.add_node_pairing(ins_node, std_node)
            return [mapping]
        return False

    # noinspection PyPep8Naming
    def shallow_match_Name(self, ins_node, std_node, check_meta=True):
        """
        Matches ins_node to std_node for different cases of encountering a name node in ins_node
            case 1: _var_ matches if std_node is a name node and automatically returns a mapping and symbol table
            case 2: __exp__ matches to any subtree and automatically returns a mapping and symbol table
            case 3: ___ matches to any subtree and automatically returns a mapping
            case 4: matches only if the exact names are the same (falls through to shallow_match_generic)
        @return a mapping of ins_node to std_node and possibly a symbol_table, or False if it doesn't match
        """
        name_id = ins_node.astNode.id
        var_match = re.compile('^_[^_].*_$')  # /regex
        exp_match = re.compile('^__.*__$')  # /regex
        wild_card = re.compile('^___$')  # /regex
        mapping = AstMap()
        matched = False
        meta_matched = self.metas_match(ins_node, std_node, check_meta)
        if var_match.match(name_id) and meta_matched:  # variable
            if type(std_node.astNode).__name__ == "Name":
                mapping.add_var_to_sym_table(ins_node, std_node)  # TODO: Capture result?
                matched = True
        # could else return False, but shallow_match_generic should do this as well
        elif exp_match.match(name_id) and meta_matched:  # expression TODO: In theory this won't run?
            mapping.add_exp_to_sym_table(ins_node, std_node)
            matched = True
        elif wild_card.match(name_id) and meta_matched:  # don't care TODO: In theory this won't run?
            matched = True

        if matched:
            mapping.add_node_pairing(ins_node, std_node)
            return [mapping]
        # else
        return self.shallow_match_generic(ins_node, std_node, check_meta)

    # noinspection PyPep8Naming,PyMethodMayBeStatic
    def shallow_match_Pass(self, ins_node, std_node, check_meta=True):
        """
        An empty body should match to anything
        :param ins_node: Instructor ast to find in the student ast
        :param std_node: Student AST to search for the instructor ast in
        :param check_meta: flag to check whether the fields of the instructor node and the student node should match
        :return: a mapping between the isntructor and student asts, or False if such a mapping doesn't exist
        """
        # if check_meta and ins_node.field != std_node.field:
        if not self.metas_match(ins_node, std_node, check_meta):
            return False
        mapping = AstMap()
        mapping.add_node_pairing(ins_node, std_node)
        return [mapping]

    # noinspection PyPep8Naming,PyMethodMayBeStatic
    def shallow_match_Expr(self, ins_node, std_node, check_meta=True):
        """
        An Expression node (not to be confused with expressions denoted by the instructor nodes in Name ast nodes)
        should match to anything
        :param ins_node: Instructor ast to find in the student ast
        :param std_node: Student AST to search for the instructor ast in
        :param check_meta: flag to check whether the fields of the instructor node and the student node should match
        :return: a mapping between the instructor and student asts, or False if such a mapping doesn't exist
        """
        # if check_meta and ins_node.field != std_node.field:
        if not self.metas_match(ins_node, std_node, check_meta):
            return False
        mapping = AstMap()
        mapping.add_node_pairing(ins_node, std_node)
        return [mapping]

    # noinspection PyMethodMayBeStatic
    def shallow_match_generic(self, ins_node, std_node, check_meta=True):
        """
        Checks that all non astNode attributes are equal between ins_node and std_node
        :param ins_node: Instructor ast root node
        :param std_node: Student AST root node
        :param check_meta: flag to check whether the fields of the instructor node and the student node should match
        :return: a mapping between the isntructor and student root nodes, or False if such a mapping doesn't exist
        """
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

            is_match = ins_field == std_field

            if not isinstance(ins_value, list):
                ins_value = [ins_value]

            if not isinstance(std_value, list):
                std_value = [std_value]

            # is_match = len(ins_value) == len(std_value)# for stretchy matching this isn't True
            # Reference ast_node_visitor.js for the original behavior and keep note of it for the purposes of handling
            # the children noting the special case when the nodes of the array are actually parameters of the node
            # (e.g. a load function) instead of a child node
            for inssub_value, stdsub_value in zip(ins_value, std_value):
                if not is_match:
                    break
                # TODO: make this a smarter comparison, maybe handle dictionaries, f-strings, tuples, etc.
                if is_primitive(inssub_value):
                    is_match = inssub_value == stdsub_value
        mapping = False
        if is_match:
            mapping = AstMap()  # return MAPPING
            mapping.add_node_pairing(ins_node, std_node)
            mapping = [mapping]
        return mapping

    # filter function for various types of nodes
    def shallow_match(self, ins_node, std_node, check_meta=True):
        method_name = 'shallow_match_' + type(ins_node.astNode).__name__
        target_func = getattr(self, method_name, self.shallow_match_generic)
        return target_func(ins_node, std_node, check_meta)

    @staticmethod
    def metas_match(ins_node, std_node, check_meta=True):
        return (check_meta and ins_node.field == std_node.field) or not check_meta or ins_node.field == "none"

    # TODO: Possibly add a feature for variable function names?

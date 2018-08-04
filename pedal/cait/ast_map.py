from pedal.cait.ct_map import *
from pedal.cait.easy_node import *


class AstSymbol:
    def __init__(self, _id="", _node=None):
        self.id = _id
        self.astNode = _node

    def __str__(self):
        return ''.join(["id = ", self.id.__str__(), ", astNode = ", type(self.astNode).__name__])

    def __repr__(self):
        return ''.join(["id = ", self.id.__str__(), ", astNode = ", type(self.astNode).__name__])


class AstMap:
    def __init__(self):
        self.mappings = CtMap()
        self.symbol_table = CtMap()
        self.exp_table = CtMap()
        self.conflict_keys = []
        self.match_root = None
        self.match_lineno = -1

    def add_var_to_sym_table(self, ins_node, std_node):
        """
        Adds ins_node.id to the symbol table if it doesn't already exist, mapping it to a set of ins_node. Updates a
        second dictionary that maps ins_node to an std_node, and overwrites the current std_node since there should only
        be one mapping.
        :param ins_node: instructor node or str representing variable
        :param std_node: student node representing variable
        :return: number of conflicts generated
        """
        if not isinstance(std_node, EasyNode):
            raise TypeError
        if isinstance(ins_node, str):
            key = ins_node
        else:
            key = ins_node.astNode.id
        value = AstSymbol(std_node.astNode.id, std_node)
        if self.symbol_table.has(key):
            new_list = self.symbol_table.get(key)
            new_list.append(value)
            if not (key in self.conflict_keys):
                for other in new_list:
                    if value.id != other.id:
                        self.conflict_keys.append(key)
                        break
        else:
            new_list = [value]

        self.symbol_table.set(key, new_list)
        return len(self.conflict_keys)

    def add_exp_to_sym_table(self, ins_node, std_node):
        """Adds mapping of expression symbol to student node
        This function does NOT check for conflicts at the moment and probably should at some point.
        TODO: Check for conflicts
        :param ins_node: Instructor node representing an expression
        :param std_node: student ast subtree corresponding to the symbol
        :return: nothing
        """
        if not isinstance(std_node, EasyNode):
            raise TypeError
        self.exp_table.set(ins_node.astNode.id, std_node)

    def add_node_pairing(self, ins_node, std_node):
        """
        Adds a mapping of instructor ast node to a specific student ast node
        :param ins_node: instructor pattern ast node
        :param std_node: student ast node
        :return: nothing
        """
        if not isinstance(std_node, EasyNode):
            raise TypeError
        self.mappings.set(ins_node, std_node)

    def has_conflicts(self, ):
        """
        :return: returns number of conflicts
        """
        return len(self.conflict_keys) > 0

    def new_merged_map(self, other):
        """
        Returns a newly merged map consisting of this and other
        without modifying self.
        :param other: (type AstMap) the other AstMap to be merged with
        :return: self modified by adding the contents of other
        """
        new_map = AstMap()
        new_map.merge_map_with(self)
        new_map.merge_map_with(other)
        return new_map

    def merge_map_with(self, other):
        """
        Returns a newly merged map consisting of this and other
        by modifying this
        :param other: (type AstMap) the other AstMap to be merged with
        :return: self modified by adding the contents of other
        """
        if type(other) != type(self):
            raise TypeError
        # merge all mappings
        other_map = other.mappings
        for other_map_key, other_map_value in zip(other_map.keys, other_map.values):
            self.mappings.set(other_map_key, other_map_value)
        # merge all expressions
        other_exp = other.exp_table
        for other_expKey, other_expValue in zip(other_exp.keys, other_exp.values):
            self.exp_table.set(other_expKey, other_expValue)
        # merge all symbols
        other_sym = other.symbol_table
        for key, value in zip(other_sym.keys, other_sym.values):
            for sub_value in value:
                self.add_var_to_sym_table(key, sub_value.astNode)

    def get_std_name(self, ins_id):
        """Return student node associated with ins_id

        :param ins_id: the instructor variable defined in the pattern
        :return: the associated student name node
        """
        if isinstance(ins_id, str):
            # noinspection PyBroadException
            try:
                return self.symbol_table.get(ins_id)
            except Exception:
                return None

    def get_exp_name(self, ins_id):
        """Return student subtree associated with ins_id

        :param ins_id: the instructor variable defined in the pattern
        :return: the associated student subtree node
        """
        if isinstance(ins_id, str):
            # noinspection PyBroadException
            try:
                return self.exp_table.get(ins_id)
            except Exception:
                return None

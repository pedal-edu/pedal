from pedal.cait.cait_node import *
from functools import reduce


class AstSymbol:
    def __init__(self, _id="", _node=None):
        self.id = _id
        self.astNode = _node
        self.ast_node = _node

    def __getattr__(self, attr):
        return getattr(self.astNode, attr)

    def __str__(self):
        # return ''.join(["id = ", self.id.__str__(), ", astNode = ", type(self.astNode).__name__])
        return self.id

    def __repr__(self):
        return ''.join(["id = ", self.id.__str__(), ", astNode = ", type(self.astNode).__name__])


class AstSymbolList:
    def __init__(self):
        self.my_list = []

    def __getitem__(self, item):
        return self.my_list.__getitem__(item)

    def append(self, item):
        self.my_list.append(item)

    def __getattr__(self, attr):
        try:
            return getattr(self.my_list[0], attr)
        except RecursionError:
            return reduce(getattr, attr.split('.'), self.my_list)

    def __len__(self):
        return self.my_list.__len__()


class AstMap:
    def __init__(self):
        self.mappings = {}
        self.symbol_table = {}
        self.exp_table = {}
        self.func_table = {}
        self.conflict_keys = []
        self.match_root = None

    def add_func_to_sym_table(self, ins_node, std_node):
        """
        Adds ins_node.name to the symbol table if it doesn't already exist, mapping it to a set of ins_node. Updates a
        second dictionary that maps ins_node to an std_node, and overwrites the current std_node since there should only
        be one mapping.
        :param ins_node: instructor node or str representing a function name
        :param std_node: student node representing function
        :return: number of conflicts generated
        """
        if not isinstance(std_node, CaitNode):
            raise TypeError
        if isinstance(ins_node, str):
            key = ins_node
        else:
            key = ins_node.astNode.name
        value = AstSymbol(std_node.astNode.name, std_node)
        if key in self.func_table:
            new_list = self.func_table[key]
            new_list.append(value)
            if not (key in self.conflict_keys):
                for other in new_list:
                    if value.name != other.name:
                        self.conflict_keys.append(key)
                        break
        else:
            new_list = AstSymbolList()
            new_list.append(value)

        self.func_table[key] = new_list
        return len(self.conflict_keys)

    def add_var_to_sym_table(self, ins_node, std_node):
        """
        Adds ins_node.id to the symbol table if it doesn't already exist, mapping it to a set of ins_node. Updates a
        second dictionary that maps ins_node to an std_node, and overwrites the current std_node since there should only
        be one mapping.
        :param ins_node: instructor node or str representing variable
        :param std_node: student node representing variable
        :return: number of conflicts generated
        """
        if not isinstance(std_node, CaitNode):
            raise TypeError
        if isinstance(ins_node, str):
            key = ins_node
        else:
            key = ins_node.astNode.id
        value = AstSymbol(std_node.astNode.id, std_node)
        if key in self.symbol_table:
            new_list = self.symbol_table[key]
            new_list.append(value)
            if not (key in self.conflict_keys):
                for other in new_list:
                    if value.id != other.id:
                        self.conflict_keys.append(key)
                        break
        else:
            new_list = AstSymbolList()
            new_list.append(value)

        self.symbol_table[key] = new_list
        return len(self.conflict_keys)

    def add_exp_to_sym_table(self, ins_node, std_node):
        """Adds mapping of expression symbol to student node
        This function does NOT check for conflicts at the moment and probably should at some point.
        TODO: Check for conflicts
        :param ins_node: Instructor node representing an expression
        :param std_node: student ast subtree corresponding to the symbol
        :return: nothing
        """
        if not isinstance(std_node, CaitNode):
            raise TypeError
        self.exp_table[ins_node.astNode.id] = std_node

    def add_node_pairing(self, ins_node, std_node):
        """
        Adds a mapping of instructor ast node to a specific student ast node
        :param ins_node: instructor pattern ast node
        :param std_node: student ast node
        :return: nothing
        """
        if not isinstance(std_node, CaitNode):
            raise TypeError
        self.mappings[ins_node] = std_node

    def has_conflicts(self):
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
        self.mappings.update(other.mappings)

        # merge all expressions
        self.exp_table.update(other.exp_table)

        # merge all symbols
        for key, value in other.symbol_table.items():
            for sub_value in value:
                self.add_var_to_sym_table(key, sub_value.astNode)

        # merge all functions
        for key, value in other.func_table.items():
            for sub_value in value:
                self.add_func_to_sym_table(key, sub_value.astNode)

    def get_std_name(self, ins_id):
        """Return student node associated with ins_id

        :param ins_id: the instructor variable defined in the pattern
        :return: the associated student name node
        """
        if isinstance(ins_id, str):
            return self.symbol_table.get(ins_id)

    def get_exp_name(self, ins_id):
        """Return student subtree associated with ins_id

        :param ins_id: the instructor variable defined in the pattern
        :return: the associated student subtree node
        """
        if isinstance(ins_id, str):
            return self.exp_table.get(ins_id)

    @property
    def match_lineno(self):
        values = [v.lineno for v in self.mappings.values()
                  if v.lineno is not None]
        if not values:
            return -1
        else:
            return min(values)

    def __getitem__(self, id):
        if id.startswith('__'):
            return self.exp_table[id]
        else:
            if id in self.symbol_table:
                return self.symbol_table[id]
            else:
                return self.func_table[id]

    def __contains__(self, id):
        if id.startswith('__'):
            return id in self.exp_table
        else:
            exists = id in self.symbol_table
            if exists:
                return exists
            else:
                return id in self.func_table

from pedal.cait.cait_node import CaitNode


class AstSymbol:
    """
    This represents an Ast symbol, whether it be a variable (name node) or a function name
    for place holders used in instructor patterns

    Notes:
        Also has the attributes of the relevant Name node from the ast class.

    Attributes:
        id (str): the name of the variable place holder used by the instructor
        ast_node (cait_node): the ast node of the variable
    """

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
    """
    This class is a wrapper for a list of AstSymbols for ease of access
    If accessed as a list, manipulable as a list, otherwise, acts as the first AstSymbol in the list
    """

    def __init__(self):
        self.my_list = []

    def __getitem__(self, item):
        return self.my_list.__getitem__(item)

    def append(self, item):
        self.my_list.append(item)

    def __getattr__(self, attr):
        return getattr(self.my_list[0], attr)

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
        self.diagnosis = ""

    def add_func_to_sym_table(self, ins_node, std_node):
        """
        Adds ins_node.name to the symbol table if it doesn't already exist, mapping it to a set of ins_node. Updates a
        second dictionary that maps ins_node to an std_node, and overwrites the current std_node since there should only
        be one mapping.

        Args:
            ins_node: instructor node or str representing a function name
            std_node: student node representing function

        Returns:
            int: number of conflicts generated

        """
        if not isinstance(std_node, CaitNode):
            raise TypeError
        if isinstance(ins_node, str):
            key = ins_node
        else:
            try:
                if ins_node.ast_name == "FunctionDef":
                    key = ins_node.astNode.name
                else:  # TODO: Little skulpt artifact that doesn't raise Attribute Errors...
                    key = ins_node.id
                    raise AttributeError
            except AttributeError:
                key = ins_node.astNode.id

        try:
            if std_node.ast_name == "FunctionDef":
                value = AstSymbol(std_node.astNode.name, std_node)
            else:  # TODO: Little skulpt artifact that doesn't raise Attribute Errors...
                raise AttributeError
#            value = AstSymbol(std_node.astNode.name, std_node)
        except AttributeError:
            node = std_node
            if type(node.astNode).__name__ != "Call":
                node = node.parent
                node.id = std_node.id
            value = AstSymbol(std_node.id, node)
        if key in self.func_table:
            new_list = self.func_table[key]
            if value not in new_list:
                new_list.append(value)
            if not (key in self.conflict_keys):
                for other in new_list:
                    if value.id != other.id:
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

        Args:
            ins_node: instructor node or str representing variable
            std_node: student node representing variable

        Returns:
            int: number of conflicts generated

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
        """
        Adds mapping of expression symbol to student node
        This function does NOT check for conflicts at the moment and probably should at some point.
        TODO: Check for conflicts
        Args:
            ins_node: Instructor node representing an expression
            std_node: student ast subtree corresponding to the symbol

        Returns:
            None
        """
        if not isinstance(std_node, CaitNode):
            raise TypeError
        self.exp_table[ins_node.astNode.id] = std_node

    def add_node_pairing(self, ins_node, std_node):
        """
        Adds a mapping of instructor ast node to a specific student ast node
        Args:
            ins_node: instructor pattern ast node
            std_node: student ast node

        Returns:
            None
        """
        if not isinstance(std_node, CaitNode):
            raise TypeError
        self.mappings[ins_node] = std_node

    def has_conflicts(self):
        """

        Returns:
            bool: True if number of conflicts is greater than 0
        """
        return len(self.conflict_keys) > 0

    def new_merged_map(self, other):
        """
        Returns a newly merged map consisting of this and other
        without modifying self.
        Args:
            other (AstMap): the other AstMap to be merged with

        Returns:
            AstMap: self modified by adding the contents of other
        """
        new_map = AstMap()
        new_map.merge_map_with(self)
        new_map.merge_map_with(other)
        return new_map

    def merge_map_with(self, other):
        """
        Returns a newly merged map consisting of this and other
        by modifying self
        Args:
            other (AstMap): the other AstMap to be merged with

        Returns:
            AstMap: self modified by adding the contents of other
        """
        if not isinstance(other, type(self)):
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
                self.add_func_to_sym_table(str(key), sub_value.astNode)

    @property
    def match_lineno(self):
        """

        Returns:
            int: the line number this match started on
        """
        values = [v.lineno for v in self.mappings.values()
                  if v.lineno is not None]
        if not values:
            return -1
        else:
            return min(values)

    def __getitem__(self, id_n):
        if id_n.startswith('__'):
            return self.exp_table[id_n]
        else:
            if id_n in self.symbol_table:
                return self.symbol_table[id_n]
            else:
                return self.func_table[id_n]

    def __contains__(self, id_n):
        if id_n.startswith('__'):
            return id_n in self.exp_table
        else:
            exists = id_n in self.symbol_table
            if exists:
                return exists
            else:
                return id_n in self.func_table

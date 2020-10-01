"""
Main TIFA visitor-based algorithm here.

TODO: JoinedStr
"""

import ast
# TODO: FileType, DayType, TimeType,
from pedal.core.commands import system_error
from pedal.core.report import MAIN_REPORT
from pedal.core.location import Location
from pedal.types.definitions import (UnknownType,
                                     FunctionType, ClassType, InstanceType,
                                     NumType, NoneType, BoolType, TupleType,
                                     ListType, StrType, GeneratorType,
                                     DictType, ModuleType, SetType,
                                     LiteralNum, LiteralBool,
                                     LiteralNone, LiteralStr,
                                     LiteralTuple, Type)
from pedal.types.normalize import (get_pedal_type_from_json,
                                   get_pedal_literal_from_pedal_type,
                                   get_pedal_type_from_annotation,
                                   get_pedal_type_from_value)
from pedal.types.builtin import (get_builtin_module, get_builtin_function)
from pedal.types.operations import (are_types_equal,
                                    VALID_UNARYOP_TYPES, VALID_BINOP_TYPES,
                                    ORDERABLE_TYPES, INDEXABLE_TYPES)
from pedal.tifa.constants import TOOL_NAME
from pedal.tifa.identifier import Identifier
from pedal.tifa.state import State
from pedal.tifa.feedbacks import (action_after_return, return_outside_function,
                                  write_out_of_scope, unconnected_blocks,
                                  iteration_problem, not_a_function,
                                  initialization_problem, unused_variable,
                                  overwritten_variable, iterating_over_non_list,
                                  iterating_over_empty_list, incompatible_types,
                                  parameter_type_mismatch, read_out_of_scope,
                                  type_changes, unnecessary_second_branch,
                                  recursive_call, multiple_return_types,
                                  possible_initialization_problem,
                                  incorrect_arity, else_on_loop_body,
                                  module_not_found, nested_function_definition,
                                  unused_returned_value, invalid_indexing, append_to_non_list)

__all__ = ['TifaCore', 'TifaAnalysis']


class TifaAnalysis:
    """
    Container class for the results of running a Tifa Analysis.

    Attributes:
        success (bool): Whether or not the analysis was able to finish.
        variables (dict): 2D Dictionary mapping (Scope Names x Variable Names)
            to their calculated types. This captures ALL the variables in
            the code (in all scopes), as opposed to just the top level
            variables.
        top_level_variables (dict): Maps variable names to their calculated
            types.
        node_types (dict): Maps AST nodes to their TIFA-calculated type.
    """
    def __init__(self):
        self.success = True
        self.error = None
        self.variables = {}
        self.top_level_variables = {}
        self.issues = {}
        self.node_types = {}

    def fail(self, error):
        """ Called when this analysis failed. """
        self.success = False
        self.error = error


class TifaCore:
    """
    TIFA Core, with methods for manipulating the TifaAnalysis data.

    Args:
        report (Report): The report object to store data and feedback in. If
                         left None, defaults to the global MAIN_REPORT.
    """
    settings: dict

    path_id: int
    scope_id: int
    ast_id: int

    path_names: list
    scope_names: list

    node_chain: list
    scope_chain: list
    path_chain: list
    definition_chain: list

    # dict[paths, dict[names, State]]
    name_map: dict
    class_scopes: dict
    path_parents: dict

    final_node: ast.AST or None

    def __init__(self, report=MAIN_REPORT):
        self.report = report
        self.settings = {}
        self.analysis = None

    def locate(self, node: ast.AST = None):
        """
        Return a dictionary representing the current location within the
        AST.

        Returns:
            Location: The line and column of the current or given node.
        """
        if node is None:
            if self.node_chain:
                node = self.node_chain[-1]
            else:
                node = self.final_node
        return Location(node.lineno+self.line_offset, col=node.col_offset)

    def _issue(self, feedback):
        if feedback.label not in self.analysis.issues:
            self.analysis.issues[feedback.label] = []
        self.analysis.issues[feedback.label].append(feedback)

    def _collect_top_level_variables(self):
        """
        Walk through the variables and add any at the top level to the
        top_level_variables field of the report.
        """
        top_level_variables = self.analysis.top_level_variables
        main_path_vars = self.name_map[self.path_chain[0]]
        for full_name in main_path_vars:
            split_name = full_name.split("/")
            if len(split_name) == 2 and split_name[0] == str(self.scope_chain[0]):
                name = split_name[1]
                top_level_variables[name] = main_path_vars[full_name]

    def reset(self):
        """
        Reinitialize fields for maintaining the system
        """
        # Unique Global IDs
        self.path_id = 0
        self.scope_id = 0
        self.ast_id = 0

        # Human readable names
        self.path_names = ['*Module']
        self.scope_names = ['*Module']
        self.node_chain = []

        # Complete record of all Names
        self.scope_chain = [self.scope_id]
        self.path_chain = [self.path_id]
        self.name_map = {self.path_id: {}}
        self.definition_chain = []
        self.path_parents = {}
        self.final_node = None
        self.class_scopes = {}

    def find_variable_scope(self, name):
        """
        Walk through this scope and all enclosing scopes, finding the relevant
        identifier given by `name`.

        Args:
            name (str): The name of the variable
        Returns:
            Identifier: An Identifier for the variable, which could potentially
                        not exist.
        """
        for scope_level, scope in enumerate(self.scope_chain):
            for path_id in self.path_chain:
                path = self.name_map[path_id]
                full_name = "/".join(map(str, self.scope_chain[scope_level:])) + "/" + name
                if full_name in path:
                    is_root_scope = (scope_level == 0)
                    return Identifier(True, is_root_scope,
                                      full_name, path[full_name])

        return Identifier(False)

    def find_variable_out_of_scope(self, name):
        """
        Walk through every scope and determine if this variable can be found
        elsewhere (which would be an issue).

        Args:
            name (str): The name of the variable
        Returns:
            Identifier: An Identifier for the variable, which could potentially
                        not exist.
        """
        for path in self.name_map.values():
            for full_name in path:
                unscoped_name = full_name.split("/")[-1]
                if name == unscoped_name:
                    return Identifier(True, False, unscoped_name, path[full_name])
        return Identifier(False)

    def find_path_parent(self, path_id, name):
        """

        Args:
            path_id:
            name:

        Returns:

        """
        if name in self.name_map[path_id]:
            return Identifier(True, state=self.name_map[path_id][name])
        else:
            path_parent = self.path_parents.get(path_id)
            if path_parent is None:
                return Identifier(False)
            else:
                return self.find_path_parent(path_parent, name)

    def _finish_scope(self):
        """
        Walk through all the variables present in this scope and ensure that
        they have been read and not overwritten.
        """
        path_id = self.path_chain[0]
        for name in self.name_map[path_id]:
            if self.in_scope(name, self.scope_chain):
                state = self.name_map[path_id][name]
                if state.over == 'yes':
                    position = state.over_position
                    self._issue(overwritten_variable(position, state.name))
                if state.read == 'no':
                    self._issue(unused_variable(state.position, state.name, state.type, report=self.report))

    def _scope_chain_str(self, name=None):
        """
        Convert the current scope chain to a string representation (divided 
        by "/").

        Returns:
            str: String representation of the scope chain.
        """
        if name:
            return "/".join(map(str, self.scope_chain)) + "/" + name
        else:
            return "/".join(map(str, self.scope_chain))

    def identify_caller(self, node):
        """
        Figures out the variable that was used to kick off this call,
        which is almost always the relevant Name to track as being updated.
        If the origin wasn't a Name, nothing will need to be updated so None
        is returned instead.

        TODO: Is this sufficient?

        Args:
            node (AST): An AST node
        Returns:
            str or None: The name of the variable or None if no origin could
                         be found.
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Call):
            return self.identify_caller(node.func)
        elif isinstance(node, (ast.Attribute, ast.Subscript)):
            return self.identify_caller(node.value)
        return None

    def iterate_variable(self, name, position=None):
        """
        Update the variable by iterating through it - this doesn't do anything
        fancy yet.
        """
        return self.load_variable(name, position)

    def store_iter_variable(self, name, new_type, position=None):
        """
        Record that the variable was iterated upon. This counts as a Read.

        Args:
            name (str): The name of the variable.
            new_type (Type): The Tifa Type of the variable.
            position: The location where this iteration occurred.

        Returns:
            :py:class:`pedal.tifa.state.State`: The wrapped State object of
                the stored variable.
        """
        state = self.store_variable(name, new_type, position)
        state.read = 'yes'
        return state

    def return_variable(self, return_type):
        """

        Args:
            return_type:

        Returns:

        """
        return self.store_variable("*return", return_type)

    def append_variable(self, name, append_type, position=None):
        """

        Args:
            name:
            append_type:
            position:

        Returns:

        """
        return self.store_variable(name, append_type, position)

    def create_variable(self, name, create_type, position=None):
        """ Stores a new variable, but unconditionally - even if it exists
        in another scope, it will be considered a new variable."""
        return self.store_variable(name, create_type, position, force_create=True)

    def store_variable(self, name, store_type, position=None, force_create=False):
        """
        Update the variable with the given name to now have the new type.

        Args:
            name (str): The unqualified name of the variable. The variable will
                        be assumed to be in the current scope.
            store_type (Type): The new type of this variable.
            position: The location that this store occurred at
        Returns:
            State: The new state of the variable.
        """
        if position is None:
            position = self.locate()
        full_name = self._scope_chain_str(name)
        current_path = self.path_chain[0]
        variable = self.find_variable_scope(name)
        if not variable.exists or force_create:
            # Create a new instance of the variable on the current path
            new_state = State(name, [], store_type, 'store', position,
                              read='no', set='yes', over='no')
            self.name_map[current_path][full_name] = new_state
        else:
            new_state = self.trace_state(variable.state, "store", position)
            if not variable.in_scope:
                self._issue(write_out_of_scope(self.locate(), name, report=self.report))
            # Type change?
            if not are_types_equal(store_type, variable.state.type):
                self._issue(type_changes(position, name, variable.state.type, store_type))
            new_state.type = store_type
            # Overwritten?
            if variable.state.set == 'yes' and variable.state.read == 'no':
                new_state.over_position = position
                new_state.over = 'yes'
            else:
                new_state.set = 'yes'
                new_state.read = 'no'
            self.name_map[current_path][full_name] = new_state
        # If this is a class scope...
        current_scope = self.scope_chain[0]
        if current_scope in self.class_scopes:
            self.class_scopes[current_scope].add_attr(name, new_state.type)
        return new_state

    def load_variable(self, name, position=None):
        """
        Retrieve the variable with the given name.

        Args:
            position:
            name (str): The unqualified name of the variable. If the variable is
                        not found in the current scope or an enclosing scope, all
                        other scopes will be searched to see if it was read out
                        of scope.
        Returns:
            State: The current state of the variable.
        """
        full_name = self._scope_chain_str(name)
        current_path = self.path_chain[0]
        variable = self.find_variable_scope(name)
        if position is None:
            position = self.locate()
        if not variable.exists:
            out_of_scope_var = self.find_variable_out_of_scope(name)
            # Create a new instance of the variable on the current path
            if out_of_scope_var.exists:
                self._issue(read_out_of_scope(self.locate(), name))
            else:
                self._issue(initialization_problem(self.locate(), name))
            new_state = State(name, [], UnknownType(), 'load', position,
                              read='yes', set='no', over='no')
            self.name_map[current_path][full_name] = new_state
        else:
            new_state = self.trace_state(variable.state, "load", position)
            if variable.state.set == 'no':
                self._issue(initialization_problem(self.locate(), name))
            if variable.state.set == 'maybe':
                if name != '*return':
                    self._issue(possible_initialization_problem(self.locate(), name))
            new_state.read = 'yes'
            if not variable.in_scope:
                self.name_map[current_path][variable.scoped_name] = new_state
            else:
                self.name_map[current_path][full_name] = new_state
        return new_state

    def load_module(self, chain):
        """
        Finds the module in the set of available modules.

        Args:
            chain (str): A chain of module imports (e.g., "matplotlib.pyplot")
        Returns:
            ModuleType: The specific module with its members, or an empty
                        module type.
        """
        module_names = chain.split('.')
        potential_module = get_builtin_module(module_names[0])
        if not isinstance(potential_module, UnknownType):
            base_module = potential_module
            for module in module_names[1:]:
                if (isinstance(base_module, ModuleType) and
                        module in base_module.submodules):
                    base_module = base_module.submodules[module]
                else:
                    self._issue(module_not_found(self.locate(), chain, False, None, report=self.report))
            return base_module
        else:
            try:
                actual_module = __import__(chain, globals(), {},
                                           ['_tifa_definitions'])
                definitions = actual_module._tifa_definitions()
                return get_pedal_type_from_json(definitions)
            except Exception as e:
                print(e)
                self._issue(module_not_found(self.locate(), chain, True, e, report=self.report))
                return ModuleType()

    def combine_states(self, left, right):
        """

        Args:
            left:
            right:

        Returns:

        """
        state = State(left.name, [left], left.type, 'branch', self.locate(),
                      read=left.read, set=left.set, over=left.over,
                      over_position=left.over_position)
        if right is None:
            state.read = 'no' if left.read == 'no' else 'maybe'
            state.set = 'no' if left.set == 'no' else 'maybe'
            state.over = 'no' if left.over == 'no' else 'maybe'
        else:
            if not are_types_equal(left.type, right.type):
                self._issue(type_changes(self.locate(), left.name, left.type, right.type))
            state.read = self.match_rso(left.read, right.read)
            state.set = self.match_rso(left.set, right.set)
            state.over = self.match_rso(left.over, right.over)
            if left.over == 'no':
                state.over_position = right.over_position
            state.trace.append(right)
        return state

    def merge_paths(self, parent_path_id, left_path_id, right_path_id):
        """
        Combines any variables on the left and right path into the parent
        name space.

        Args:
            parent_path_id (int): The parent path of the left and right branches
            left_path_id (int): One of the two paths
            right_path_id (int): The other of the two paths.
        """
        # Combine two paths into one
        # Check for any names that are on the IF path
        for left_name in self.name_map[left_path_id]:
            left_state = self.name_map[left_path_id][left_name]
            right_identifier = self.find_path_parent(right_path_id, left_name)
            if right_identifier.exists:
                # Was on both IF and ELSE path
                right_state = right_identifier.state
            else:
                # Was only on IF path, potentially on the parent path
                right_state = self.name_map[parent_path_id].get(left_name)
            combined = self.combine_states(left_state, right_state)
            self.name_map[parent_path_id][left_name] = combined
        # Check for names that are on the ELSE path but not the IF path
        for right_name in self.name_map[right_path_id]:
            if right_name not in self.name_map[left_path_id]:
                right_state = self.name_map[right_path_id][right_name]
                # Potentially on the parent path
                parent_state = self.name_map[parent_path_id].get(right_name)
                combined = self.combine_states(right_state, parent_state)
                self.name_map[parent_path_id][right_name] = combined

    @staticmethod
    def trace_state(state, method, position):
        """
        Makes a copy of the given state with the given method type.

        Args:
            state (State): The state to copy (as in, we trace a copy of it!)
            method (str): The operation being applied to the state.
            position: The location this copy occurred at.
        Returns:
            State: The new State
        """
        return state.copy(method, position)

    @staticmethod
    def in_scope(full_name, scope_chain):
        """
        Determine if the fully qualified variable name is in the given scope
        chain.

        Args:
            full_name (str): A fully qualified variable name
            scope_chain (list): A representation of a scope chain.
        Returns:
            bool: Whether the variable lives in this scope
        """
        # Get this entity's full scope chain
        name_scopes = full_name.split("/")[:-1]
        # against the reverse scope chain
        checking_scopes = [str(s) for s in scope_chain]
        return name_scopes == checking_scopes

    @staticmethod
    def match_rso(left, right):
        """

        Args:
            left:
            right:

        Returns:

        """
        if left == right:
            return left
        else:
            return "maybe"

    def get_literal(self, node):
        """

        Args:
            node:

        Returns:

        """
        if isinstance(node, ast.Num):
            return LiteralNum(node.n)
        elif isinstance(node, ast.Str):
            return LiteralStr(node.s)
        elif isinstance(node, ast.Tuple):
            values = []
            for elt in node.elts:
                subvalue = self.get_literal(elt)
                if subvalue is not None:
                    values.append(subvalue)
                else:
                    return None
            return LiteralTuple(values)
        elif isinstance(node, ast.Name):
            if node.id == "None":
                return LiteralNone(None)
            elif node.id == "False":
                return LiteralBool(False)
            elif node.id == "True":
                return LiteralBool(True)
        return None

    def check_common_bad_lookups(self, left_type, attr, node):
        """ Handle common kinds of bad lookups, like appending to a non-list. """
        if attr == "append":
            if not isinstance(left_type, ListType):
                self._issue(append_to_non_list(self.locate(node),
                                               self.identify_caller(node),
                                               left_type,
                                               report=self.report))

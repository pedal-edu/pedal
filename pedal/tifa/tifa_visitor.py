


"""
Main TIFA visitor-based algorithm here.

TODO: JoinedStr
"""

import ast
# TODO: FileType, DayType, TimeType,
from pedal.core.commands import system_error
from pedal.tifa.tifa_core import TifaCore, TifaAnalysis
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
from pedal.tifa.contexts import NewPath, NewScope
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
                                  unused_returned_value, invalid_indexing)
from pedal.utilities.system import IS_PYTHON_39


class Tifa(TifaCore, ast.NodeVisitor):
    """
    TIFA subclass for traversing an AST and finding common issues.
    You can instantiate this class, manipulate settings, and then process
    some code or AST.
    """

    def process_code(self, code, filename=None, reset=True):
        """
        Processes the AST of the given source code to generate a report.

        Args:
            code (str): The Python source code
            filename (str): The filename of the source code (defaults to
                the submissions' main file).
            reset (bool): Whether or not to reset the results from the
                previous analysis before running this one.
        Returns:
            Report: The successful or successful report object
        """
        if reset or self.analysis is None:
            self.analysis = TifaAnalysis()
        filename = filename or self.report.submission.main_file
        self.line_offset = self.report.submission.line_offsets.get(filename, 0)

        # Attempt parsing - might fail!
        try:
            ast_tree = ast.parse(code, filename)
        except Exception as error:
            self.analysis.fail(error)
            system_error(TOOL_NAME, "Could not parse code: " + str(error),
                         report=self.report)
            return self.analysis
        # Attempt processing code - might fail!
        try:
            self.process_ast(ast_tree)
        except Exception as error:
            self.analysis.fail(error)
            system_error(TOOL_NAME, "Successfully parsed but could not "
                                    "process AST: " + str(error),
                         report=self.report)
        # Return whatever we got
        return self.analysis

    def process_ast(self, ast_tree):
        """
        Given an AST, actually performs the type and flow analyses to return a
        report.

        Args:
            ast_tree (AST): The AST object
        """
        self.reset()
        # Traverse every node
        self.visit(ast_tree)

        # Update analysis, finish out the current scope.
        self.analysis.variables = self.name_map
        self._finish_scope()

        # Collect top level variables
        self._collect_top_level_variables()

        return self.analysis

    def visit(self, node):
        """
        Process this node by calling its appropriate visit_*

        Args:
            node (AST): The node to visit
        Returns:
            Type: The type calculated during the visit.
        """
        # Start processing the node
        self.node_chain.append(node)
        self.ast_id += 1

        # Actions after return?
        if len(self.scope_chain) > 1:
            return_state = self.find_variable_scope("*return")
            if return_state.exists and return_state.in_scope:
                if return_state.state.set == "yes":
                    self._issue(action_after_return(self.locate(),
                                                    report=self.report))

        # No? All good, let's enter the node
        self.final_node = node
        result = ast.NodeVisitor.visit(self, node)
        # If a node failed to return something, return the UNKNOWN TYPE
        if result is None:
            result = UnknownType()
        self.analysis.node_types[node] = result

        # Pop the node out of the chain
        self.ast_id -= 1
        self.node_chain.pop()

        return result

    def _visit_nodes(self, nodes):
        """
        Visit all the nodes in the given list.

        Args:
            nodes (list): A list of values, of which any AST nodes will be
                          visited.
        """
        for node in nodes:
            if isinstance(node, ast.AST):
                self.visit(node)

    @staticmethod
    def walk_targets(targets, target_type, walker):
        """
        Iterate through the targets and call the given function on each one.

        Args:
            targets (list of Ast nodes): A list of potential targets to be
                                         traversed.
            target_type (Type): The given type to be unraveled and applied to the
                         targets.
            walker (Ast Node, Type -> None): A function that will process
                                             each target and unravel the type.
        """
        for target in targets:
            walker(target, target_type)

    def _walk_target(self, target, target_type):
        """
        Recursively apply the type to the target

        Args:
            target (Ast): The current AST node to process
            target_type (Type): The type to apply to this node
        """
        if isinstance(target, ast.Name):
            self.store_iter_variable(target.id, target_type, self.locate(target))
            return target.id
        elif isinstance(target, (ast.Tuple, ast.List)):
            result = None
            for i, elt in enumerate(target.elts):
                elt_type = target_type.iterate(LiteralNum(i))
                potential_name = self._walk_target(elt, elt_type)
                if potential_name is not None and result is None:
                    result = potential_name
            return result

    # TODO: Properly handle assignments with subscripts
    def assign_target(self, target, target_type):
        """
        Assign the type to the target, handling all kinds of assignment
        statements, including Names, Tuples/Lists, Subscripts, and
        Attributes.

        Args:
            target (ast.AST): The target AST Node.
            target_type (Type): The TIFA type.

        Returns:

        """
        if isinstance(target, ast.Name):
            self.store_variable(target.id, target_type)
        elif isinstance(target, (ast.Tuple, ast.List)):
            for i, elt in enumerate(target.elts):
                elt_type = target_type.iterate(LiteralNum(i))
                self.assign_target(elt, elt_type)
        elif isinstance(target, ast.Subscript):
            left_hand_type = self.visit(target.value)
            if isinstance(left_hand_type, ListType):
                # TODO: Handle updating value in list
                pass
            elif isinstance(left_hand_type, DictType):
                # TODO: Update this for Python 3.9, now that Slice notation has changed
                if not isinstance(target.slice, ast.Index):
                    # TODO: Can't subscript a dictionary assignment
                    return None
                literal = self.get_literal(target.slice.value)
                if not literal:
                    key_type = self.visit(target.slice.value)
                    left_hand_type.empty = False
                    left_hand_type.keys = [key_type.clone()]
                    left_hand_type.values = [target_type.clone()]
                elif left_hand_type.literals:
                    original_type = left_hand_type.has_literal(literal)
                    if not original_type:
                        left_hand_type.update_key(literal, target_type.clone())
                    elif not are_types_equal(original_type, target_type):
                        # TODO: Fix "Dictionary" to be the name of the variable
                        self._issue(type_changes(self.locate(), 'Dictionary', original_type, target_type))
        elif isinstance(target, ast.Attribute):
            left_hand_type = self.visit(target.value)
            if isinstance(left_hand_type, InstanceType):
                left_hand_type.add_attr(target.attr, target_type)
            # TODO: Otherwise we attempted to assign to a non-instance
            # TODO: Handle minor type changes (e.g., appending to an inner list)

    def _visit_collection_loop(self, node):
        was_empty = False
        # Handle the iteration list
        iter_list = node.iter
        iter_list_name = None
        if isinstance(iter_list, ast.Name):
            iter_list_name = iter_list.id
            if iter_list_name == "___":
                self._issue(unconnected_blocks(self.locate(iter_list), report=self.report))
            state = self.iterate_variable(iter_list_name, self.locate(iter_list))
            iter_type = state.type
        else:
            iter_type = self.visit(iter_list)

        if iter_type.is_empty():
            # TODO: It should check if its ONLY ever iterating over an empty list.
            # For now, only reports if we are NOT in a function
            was_empty = True
            if len(self.scope_chain) == 1:
                self._issue(iterating_over_empty_list(self.locate(iter_list), iter_list_name))

        if not isinstance(iter_type, INDEXABLE_TYPES):
            self._issue(iterating_over_non_list(self.locate(iter_list), iter_list_name, report=self.report))

        iter_subtype = iter_type.iterate(LiteralNum(0))

        # Handle the iteration variable
        iter_variable_name = self._walk_target(node.target, iter_subtype)

        # Check that the iteration list and variable are distinct
        if iter_variable_name and iter_list_name:
            if iter_variable_name == iter_list_name:
                self._issue(iteration_problem(self.locate(node.target), iter_variable_name))

        return was_empty

    def visit_AnnAssign(self, node):
        """
        TODO: Implement!
        """
        # Name, Attribute, or SubScript
        target = node.target
        # Type
        annotation = node.annotation
        # Optional assigned value
        value = node.value
        # 0 or 1, with 1 indicating pure names (not expressions)
        simple = node.simple
        # If it's a class attribute, then build up the type!
        if simple:
            self.visit(annotation)
            annotation = get_pedal_type_from_annotation(annotation, self)
            current_scope = self.scope_chain[0]
            if current_scope in self.class_scopes:
                # TODO: Treat it as a different kind of ClassType? TypedDict?
                self.class_scopes[current_scope].add_attr(target.id, annotation)

    def visit_Expr(self, node):
        """
        Any expression being used as a statement.

        Args:
            node (AST): An Expr node

        Returns:

        """
        value = self.visit(node.value)
        if isinstance(node.value, ast.Call) and not isinstance(value, NoneType):
            # TODO: Helper function to get name with title ("append method")
            if isinstance(node.value.func, ast.Name):
                call_type = 'function'
            else:
                call_type = 'method'
            name = self.identify_caller(node.value)
            self._issue(unused_returned_value(self.locate(), name,
                                              call_type, value))

    def visit_Assign(self, node):
        """
        Simple assignment statement:
        __targets__ = __value__

        Args:
            node (AST): An Assign node
        Returns:
            None
        """
        # Handle value
        value_type = self.visit(node.value)
        # Handle targets
        self._visit_nodes(node.targets)

        self.walk_targets(node.targets, value_type, self.assign_target)

    def visit_AugAssign(self, node):
        """

        Args:
            node:

        Returns:

        """
        # Handle value
        right = self.visit(node.value)
        # Handle target
        left = self.visit(node.target)
        # Target is always a Name, Subscript, or Attribute
        name = self.identify_caller(node.target)

        # Handle operation
        self.load_variable(name)
        if isinstance(left, UnknownType) or isinstance(right, UnknownType):
            return UnknownType()
        elif type(node.op) in VALID_BINOP_TYPES:
            op_lookup = VALID_BINOP_TYPES[type(node.op)]
            if type(left) in op_lookup:
                op_lookup = op_lookup[type(left)]
                if type(right) in op_lookup:
                    op_lookup = op_lookup[type(right)]
                    result_type = op_lookup(left, right)
                    self.assign_target(node.target, result_type)
                    return result_type
        self._issue(incompatible_types(self.locate(), node.op, left, right, report=self.report))

    def visit_Attribute(self, node):
        """

        Args:
            node:

        Returns:

        """
        # Handle value
        value_type = self.visit(node.value)
        self.check_common_bad_lookups(value_type, node.attr, node.value)
        # Handle ctx
        # TODO: Handling contexts
        # Handle attr
        result = value_type.load_attr(node.attr)
        return result

    def visit_BinOp(self, node):
        """

        Args:
            node:

        Returns:

        """
        # Handle left and right
        left = self.visit(node.left)
        right = self.visit(node.right)

        # Handle operation
        if isinstance(left, UnknownType) or isinstance(right, UnknownType):
            return UnknownType()
        elif type(node.op) in VALID_BINOP_TYPES:
            op_lookup = VALID_BINOP_TYPES[type(node.op)]
            if type(left) in op_lookup:
                op_lookup = op_lookup[type(left)]
                if type(right) in op_lookup:
                    op_lookup = op_lookup[type(right)]
                    return op_lookup(left, right)
        self._issue(incompatible_types(self.locate(), node.op, left, right, report=self.report))
        return UnknownType()

    def visit_Bool(self, node):
        """
        Visit a constant boolean value.

        Args:
            node (ast.AST): The boolean value Node.

        Returns:
            Type: A Bool type.
        """
        return BoolType()

    def visit_BoolOp(self, node):
        """

        Args:
            node:

        Returns:

        """
        # Handle left and right
        values = []
        for value in node.values:
            values.append(self.visit(value))

        # TODO: Truthiness is not supported! Probably need a Union type
        # TODO: Literals used as truthy value

        # Handle operation
        return BoolType()

    def visit_Call(self, node):
        """

        Args:
            node:

        Returns:

        """
        # Handle func part (Name or Attribute)
        function_type = self.visit(node.func)
        # TODO: Need to grab the actual type in some situations
        callee = self.identify_caller(node)

        # Handle args
        arguments = [self.visit(arg) for arg in node.args] if node.args else []

        # Check special common mistakes

        # TODO: Handle keywords
        # TODO: Handle star args
        # TODO: Handle kwargs
        if isinstance(function_type, FunctionType):
            # Test if we have called this definition before
            if function_type.definition not in self.definition_chain:
                self.definition_chain.append(function_type.definition)
                # Function invocation
                result = function_type.definition(self, function_type, callee,
                                                  arguments, self.locate())
                self.definition_chain.pop()
                return result
            else:
                self._issue(recursive_call(self.locate(), callee, report=self.report))
        elif isinstance(function_type, ClassType):
            constructor = function_type.get_constructor().definition
            self.definition_chain.append(constructor)
            result = constructor(self, constructor, callee, arguments, self.locate())
            self.definition_chain.pop()
            if '__init__' in function_type.fields:
                initializer = function_type.fields['__init__']
                if isinstance(initializer, FunctionType):
                    self.definition_chain.append(initializer)
                    initializer.definition(self, initializer, result, [result] + arguments, self.locate())
                    self.definition_chain.pop()
            return result
        elif isinstance(function_type, (NumType, StrType, BoolType, NoneType)):
            self._issue(not_a_function(self.locate(), callee, function_type, report=self.report))
        return UnknownType()

    def visit_ClassDef(self, node):
        """

        Args:
            node:
        """
        class_name = node.name
        new_class_type = ClassType(class_name)
        self.store_variable(class_name, new_class_type)
        # TODO: Define a new scope definition that executes the body
        # TODO: find __init__, execute that
        # TODO: handle Record subclasses
        definitions_scope = self.scope_chain[:]
        class_scope = NewScope(self, definitions_scope, class_type=new_class_type)
        with class_scope:
            self.generic_visit(node)

    def visit_Compare(self, node):
        """

        Args:
            node:

        Returns:

        """
        # Handle left and right
        left = self.visit(node.left)
        comparators = [self.visit(compare) for compare in node.comparators]

        # Handle ops
        for op, right in zip(node.ops, comparators):
            if isinstance(op, (ast.Eq, ast.NotEq, ast.Is, ast.IsNot)):
                continue
            elif isinstance(op, (ast.Lt, ast.LtE, ast.GtE, ast.Gt)):
                if are_types_equal(left, right):
                    if isinstance(left, ORDERABLE_TYPES):
                        continue
            elif isinstance(op, (ast.In, ast.NotIn)):
                if isinstance(right, INDEXABLE_TYPES):
                    continue
            self._issue(incompatible_types(self.locate(), op, left, right, report=self.report))
        return BoolType()

    def visit_comprehension(self, node):
        """

        Args:
            node:
        """
        self._visit_collection_loop(node)
        # Handle ifs, unless they're blank (None in Skulpt :)
        if node.ifs:
            self.visit_statements(node.ifs)

    def visit_Dict(self, node):
        """
        Three types of dictionaries
        - empty
        - uniform type
        - record
        TODO: Handle records appropriately
        """
        result_type = DictType()
        if not node.keys:
            result_type.empty = True
        else:
            result_type.empty = False
            all_literals = True
            keys, values, literals = [], [], []
            for key, value in zip(node.keys, node.values):
                literal = self.get_literal(key)
                key, value = self.visit(key), self.visit(value)
                values.append(value)
                keys.append(key)
                if literal is not None:
                    literals.append(literal)
                else:
                    all_literals = False

            if all_literals:
                result_type.literals = literals
                result_type.values = values
            else:
                result_type.keys = node.keys[0]
                result_type.values = node.values[0]
        return result_type

    def visit_DictComp(self, node):
        """

        Args:
            node:

        Returns:

        """
        # TODO: Handle comprehension scope
        for generator in node.generators:
            self.visit(generator)
        keys = self.visit(node.key)
        values = self.visit(node.value)
        return DictType(keys=keys, values=values)

    def visit_For(self, node):
        """

        Args:
            node:
        """
        was_empty = self._visit_collection_loop(node)
        # Handle the bodies
        #if not was_empty:
        #this_path_id = self.path_chain[0]
        #non_empty_path = NewPath(self, this_path_id, "f")
        #with non_empty_path:
        self.visit_statements(node.body)
        self.visit_statements(node.orelse)

    def visit_FunctionDef(self, node):
        """

        Args:
            node:

        Returns:

        """
        # Name
        function_name = node.name
        position = self.locate()
        definitions_scope = self.scope_chain[:]

        def definition(tifa, call_type, call_name, parameters, call_position):
            """

            Args:
                tifa:
                call_type:
                call_name:
                parameters:
                call_position:

            Returns:

            """
            function_scope = NewScope(self, definitions_scope)
            with function_scope:
                # Process arguments
                args = node.args.args
                if len(args) != len(parameters):
                    self._issue(incorrect_arity(self.locate(), function_name, report=self.report))
                # TODO: Handle special types of parameters
                for arg, parameter in zip(args, parameters):
                    name = arg.arg
                    if arg.annotation:
                        self.visit(arg.annotation)
                        annotation = get_pedal_type_from_annotation(arg.annotation, self)
                        # TODO: Use parameter information to "fill in" empty lists
                        if isinstance(parameter, ListType) and isinstance(annotation, ListType):
                            if isinstance(parameter.subtype, UnknownType):
                                parameter.subtype = annotation.subtype
                        # TODO: Check that arg.type and parameter type match!
                        if not are_types_equal(annotation, parameter, True):
                            self._issue(parameter_type_mismatch(self.locate(), name, annotation, parameter))
                    if parameter is not None:
                        parameter = parameter.clone_mutably()
                        self.create_variable(name, parameter, position)
                # Too many arguments
                if len(args) < len(parameters):
                    for undefined_parameter in parameters[len(args):]:
                        self.create_variable(name, UnknownType(), position)
                # Not enough arguments
                if len(args) > len(parameters):
                    for arg in args[len(parameters):]:
                        if arg.annotation:
                            self.visit(arg.annotation)
                            annotation = get_pedal_type_from_annotation(arg.annotation, self)
                        else:
                            annotation = UnknownType()
                        self.create_variable(arg.arg, annotation, position)
                self.visit_statements(node.body)
                return_state = self.find_variable_scope("*return")
                return_value = NoneType()
                # TODO: Figure out if we are not returning something when we should
                # If the pseudo variable exists, we load it and get its type
                if return_state.exists and return_state.in_scope:
                    return_state = self.load_variable("*return", call_position)
                    return_value = return_state.type
                    if node.returns:
                        # self.visit(node.returns)
                        returns = get_pedal_type_from_annotation(node.returns, self)
                        if not are_types_equal(return_value, returns, True):
                            self._issue(multiple_return_types(return_state.position,
                                                              returns.precise_description(),
                                                              return_value.precise_description(),
                                                              report=self.report))
            return return_value

        function = FunctionType(definition=definition, name=function_name)
        self.store_variable(function_name, function)

        if len(self.node_chain) > 2:
            self._issue(nested_function_definition(self.locate(), function_name))

        return function

    def visit_GeneratorExp(self, node):
        """

        Args:
            node:

        Returns:

        """
        # TODO: Handle comprehension scope
        for generator in node.generators:
            self.visit(generator)
        return GeneratorType(self.visit(node.elt))

    def visit_If(self, node):
        """

        Args:
            node:
        """
        # Visit the conditional
        self.visit(node.test)

        if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.Pass):
            self._issue(unnecessary_second_branch(self.locate()))
        elif len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            if node.orelse:
                self._issue(unnecessary_second_branch(self.locate()))

        # Visit the bodies
        this_path_id = self.path_chain[0]
        if_path = NewPath(self, this_path_id, "i")
        with if_path:
            for statement in node.body:
                self.visit(statement)
        else_path = NewPath(self, this_path_id, "e")
        with else_path:
            for statement in node.orelse:
                self.visit(statement)

        # TODO: Unconditional return

        # Combine two paths into one
        # Check for any names that are on the IF path
        self.merge_paths(this_path_id, if_path.id, else_path.id)

    def visit_IfExp(self, node):
        """

        Args:
            node:

        Returns:

        """
        # Visit the conditional
        self.visit(node.test)

        # Visit the body
        body = self.visit(node.body)

        # Visit the orelse
        orelse = self.visit(node.orelse)

        if are_types_equal(body, orelse):
            return body

        # TODO: Union type?
        return UnknownType()

    def visit_Import(self, node):
        """

        Args:
            node:
        """
        # Handle names
        for alias in node.names:
            asname = alias.asname or alias.name
            module_type = self.load_module(alias.name)
            self.store_variable(asname, module_type)

    def visit_ImportFrom(self, node):
        """

        Args:
            node:
        """
        # Handle names
        for alias in node.names:
            if node.module is None:
                asname = alias.asname or alias.name
                module_type = self.load_module(alias.name)
            else:
                module_name = node.module
                asname = alias.asname or alias.name
                module_type = self.load_module(module_name)
            name_type = module_type.load_attr(alias.name)
            self.store_variable(asname, name_type)

    def visit_Lambda(self, node):
        """

        Args:
            node:

        Returns:

        """
        # Name
        position = self.locate()
        definitions_scope = self.scope_chain[:]

        def definition(tifa, call_type, call_name, parameters, call_position):
            """

            Args:
                tifa:
                call_type:
                call_name:
                parameters:
                call_position:

            Returns:

            """
            function_scope = NewScope(self, definitions_scope)
            with function_scope:
                # Process arguments
                args = node.args.args
                if len(args) != len(parameters):
                    self._issue(incorrect_arity(position, "lambda", report=self.report))
                # TODO: Handle special types of parameters
                for arg, parameter in zip(args, parameters):
                    name = arg.arg
                    if parameter is not None:
                        parameter = parameter.clone_mutably()
                        self.store_variable(name, parameter, position)
                if len(args) < len(parameters):
                    for undefined_parameter in parameters[len(args):]:
                        self.store_variable(name, UnknownType(), position)
                return_value = self.visit(node.body)
            return return_value

        return FunctionType(definition=definition)

    def visit_List(self, node):
        """

        Args:
            node:

        Returns:

        """
        result_type = ListType()
        if node.elts:
            result_type.empty = False
            # TODO: confirm homogenous subtype
            for elt in node.elts:
                result_type.subtype = self.visit(elt)
        else:
            result_type.empty = True
        return result_type

    def visit_ListComp(self, node):
        """

        Args:
            node:

        Returns:

        """
        # TODO: Handle comprehension scope
        for generator in node.generators:
            self.visit(generator)
        return ListType(self.visit(node.elt))

    def visit_NameConstant(self, node):
        """

        Args:
            node:

        Returns:

        """
        value = node.value
        if isinstance(value, bool):
            return BoolType()
        else:
            return NoneType()

    def visit_Name(self, node):
        """

        Args:
            node:

        Returns:

        """
        name = node.id
        if name == "___":
            self._issue(unconnected_blocks(self.locate()))
        if isinstance(node.ctx, ast.Load):
            if name == "True" or name == "False":
                return BoolType()
            elif name == "None":
                return NoneType()
            else:
                variable = self.find_variable_scope(name)
                builtin = get_builtin_function(name)
                if not variable.exists and builtin:
                    return builtin
                else:
                    state = self.load_variable(name)
                    return state.type
        else:
            variable = self.find_variable_scope(name)
            if variable.exists:
                return variable.state.type
            else:
                return UnknownType()

    def visit_Num(self, node):
        """

        Args:
            node:

        Returns:

        """
        return NumType()

    def visit_Constant(self, node) -> Type:
        """ Handle new 3.8's Constant node """
        return get_pedal_type_from_value(node.value)

    def visit_Return(self, node):
        """

        Args:
            node:
        """
        if len(self.scope_chain) == 1:
            self._issue(return_outside_function(self.locate(), report=self.report))
        # TODO: Unconditional return inside loop
        if node.value is not None:
            self.return_variable(self.visit(node.value))
        else:
            self.return_variable(NoneType())

    def visit_Set(self, node):
        # Fun fact, it's impossible to make a literal empty set
        return SetType(subtype=self.visit(node.elts[0]), empty=False)

    def visit_SetComp(self, node):
        """

        Args:
            node:

        Returns:

        """
        # TODO: Handle comprehension scope
        for generator in node.generators:
            self.visit(generator)
        return SetType(subtype=self.visit(node.elt))

    def visit_statements(self, nodes):
        """

        Args:
            nodes:

        Returns:

        """
        # TODO: Check for pass in the middle of a series of statement
        if any(isinstance(node, ast.Pass) for node in nodes):
            pass
        return [self.visit(statement) for statement in nodes]

    def visit_Str(self, node):
        """

        Args:
            node:

        Returns:

        """
        if node.s == "":
            return StrType(True)
        else:
            return StrType(False)

    def visit_JoinedStr(self, node):
        values = [self.visit(expr) for expr in node.values]
        # The result will be all StrType
        return StrType(empty=all(n.empty for n in values))

    def visit_FormattedValue(self, node):
        value = self.visit(node.value)
        if isinstance(value, StrType):
            return value
        else:
            return StrType(empty=False)

    def visit_Subscript(self, node):
        """

        Args:
            node:

        Returns:

        """
        # Handle value
        value_type = self.visit(node.value)
        # Handle slice
        if IS_PYTHON_39 and isinstance(node.slice, ast.Tuple):
            # TODO: Do something about extslices (especially since students stumble into this accidentally)
            pass
        elif not IS_PYTHON_39 and isinstance(node.slice, ast.ExtSlice):
            # TODO: Do something about extslices (especially since students stumble into this accidentally)
            pass
        elif isinstance(node.slice, ast.Slice):
            self.visit_Slice(node.slice)
            return value_type
        else:
            if IS_PYTHON_39:
                slice = node.slice
            else:
                slice = node.slice.value
            literal = self.get_literal(slice)
            if literal is None:
                literal = get_pedal_literal_from_pedal_type(self.visit(slice))
            result = value_type.index(literal)
            # TODO: Is this sufficient? Maybe we should be throwing?
            if isinstance(result, UnknownType):
                self._issue(invalid_indexing(self.locate(), value_type,
                                             literal.type()))
            else:
                return result

    def visit_Slice(self, node):
        """ Handles a slice by visiting its components; cannot return a value
        because the slice is always the same type as its value, which is
        not available on the Slice node itself. """
        if node.lower is not None:
            self.visit(node.lower)
        if node.upper is not None:
            self.visit(node.upper)
        if node.step is not None:
            self.visit(node.step)

    def visit_Tuple(self, node) -> TupleType:
        """ Handle Tuple literal """
        result_type = TupleType()
        if not node.elts:
            result_type.empty = True
            result_type.subtypes = []
        else:
            result_type.empty = False
            # TODO: confirm homogenous subtype
            result_type.subtypes = [self.visit(elt) for elt in node.elts]
        return result_type

    def visit_UnaryOp(self, node):
        """

        Args:
            node:

        Returns:

        """
        # Handle operand
        operand = self.visit(node.operand)

        if isinstance(node.op, ast.Not):
            return BoolType()
        elif isinstance(operand, UnknownType):
            return UnknownType()
        elif type(node.op) in VALID_UNARYOP_TYPES:
            op_lookup = VALID_UNARYOP_TYPES[type(node.op)]
            if type(operand) in op_lookup:
                return op_lookup[type(operand)]()
        return UnknownType()

    def visit_While(self, node):
        """

        Args:
            node:
        """
        # Visit conditional
        self.visit(node.test)

        # Visit the bodies
        this_path_id = self.path_id
        # One path is that we never enter the body
        empty_path = NewPath(self, this_path_id, "e")
        with empty_path:
            pass
        # Another path is that we loop through the body and check the test again
        body_path = NewPath(self, this_path_id, "w")
        with body_path:
            for statement in node.body:
                self.visit(statement)
            # Revisit conditional
            self.visit(node.test)
        # If there's else bodies (WEIRD) then we should check them afterwards
        if node.orelse:
            self._issue(else_on_loop_body(self.locate()))
            for statement in node.orelse:
                self.visit(statement)

        # Combine two paths into one
        # Check for any names that are on the IF path
        self.merge_paths(this_path_id, body_path.id, empty_path.id)

    def visit_With(self, node):
        """

        Args:
            node:
        """
        for item in node.items:
            type_value = self.visit(item.context_expr)
            self.visit(item.optional_vars)
            self._walk_target(item.optional_vars, type_value)
        # Handle the bodies
        self.visit_statements(node.body)

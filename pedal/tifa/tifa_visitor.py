
"""
Main TIFA visitor-based algorithm here.

TODO: JoinedStr
"""

import ast
# TODO: FileType, DayType, TimeType,
from pedal.core.commands import system_error
from pedal.tifa.tifa_core import TifaCore, TifaAnalysis
from pedal.types.new_types import (Type, AnyType, ImpossibleType, FunctionType, GeneratorType,
                                   IntType, FloatType, BoolType, TupleType,
                                   ListType, StrType, SetType, DictType,
                                   ClassType, InstanceType, BuiltinConstructorType, NumType, NoneType,
                                   LiteralValue, LiteralInt, LiteralFloat, LiteralStr, LiteralBool,
                                   TypeUnion, widen_type, widest_type)
from pedal.types.new_types import is_subtype, specify_subtype
from pedal.types.normalize import get_pedal_type_from_value
from pedal.types.builtin import get_builtin_name
from pedal.types.operations import (VALID_UNARYOP_TYPES, apply_binary_operation, apply_unary_operation)
from pedal.tifa.constants import TOOL_NAME
from pedal.tifa.contexts import NewPath, NewScope
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
                                  unused_returned_value, invalid_indexing,
                                  attribute_type_change)
from pedal.utilities.system import IS_AT_LEAST_PYTHON_38


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
        filename = filename or (self.report.submission.main_file if self.report.submission else 'student.py')
        self.line_offset = self.report.submission.line_offsets.get(filename, 0) if self.report.submission else 0

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
            system_error(TOOL_NAME, message="Successfully parsed but could not "
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
            result = AnyType()
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

        if iter_type.is_empty:
            # TODO: It should check if its ONLY ever iterating over an empty list.
            # For now, only reports if we are NOT in a function
            was_empty = True
            if len(self.scope_chain) == 1:
                self._issue(iterating_over_empty_list(self.locate(iter_list), iter_list_name))

        iter_subtype = iter_type.iterate()
        if isinstance(iter_subtype, ImpossibleType):
            self._issue(iterating_over_non_list(self.locate(iter_list), iter_list_name, report=self.report))


        # Handle the iteration variable
        self.assign_target(node.target, iter_subtype, store_with_read=True)

        # Check that the iteration list and variable are distinct
        if isinstance(node.target, ast.Name) and node.target.id == iter_list_name:
            self._issue(iteration_problem(self.locate(node.target), node.target.id))

        return was_empty

    def break_starred(self, elements):
        leading, starred, trailing = [], [], []
        all_elements = iter(elements)
        for elt in all_elements:
            if isinstance(elt, ast.Starred):
                starred.append(elt)
                break
            else:
                leading.append(elt)
        else:
            return leading, starred, trailing
        for elt in all_elements:
            trailing.append(elt)
        return leading, starred, trailing

    # TODO: Properly handle assignments with subscripts
    def assign_target(self, target, target_type, operation=None, store_with_read=False):
        """
        Assign the type to the target, handling all kinds of assignment
        statements, including Names, Tuples/Lists, Subscripts, and
        Attributes.

        Args:
            target (ast.AST): The target AST Node.
            target_type (Type): The new TIFA type.
            operation (None | ast.op): The AugAssign operation, if there is one
            store_with_read: Whether to store the variable as a read variable, or just a write variable.

        Returns:

        """
        if isinstance(target, ast.Name):
            original_value_type = self.visit(target)
            if operation:
                new_target_type = apply_binary_operation(operation, original_value_type, target_type)
                if isinstance(new_target_type, ImpossibleType):
                    self._issue(incompatible_types(self.locate(), operation, original_value_type, target_type, report=self.report))
            else:
                new_target_type = target_type
            if store_with_read:
                self.store_read_variable(target.id, new_target_type)
            else:
                self.store_variable(target.id, new_target_type)
        elif isinstance(target, (ast.Tuple, ast.List)):
            original_type = self.visit(target)
            leading, starred, trailing = self.break_starred(target.elts)
            tt, ot = target_type.break_apart(), original_type.break_apart()
            for elt, elt_type, old_type in zip(leading, tt, ot):
                self.assign_target(elt, elt_type)
            if starred:
                # TODO: Handle starred node's type changes
                # if not is_subtype(target_type, old_type):
                    # self._issue(type_changes(self.locate(), 'an element of NODE', old_type.singular_name, elt_type.singular_name))
                self.assign_target(starred[0], target_type)
                for elt, elt_type, old_type in zip(trailing, tt, ot):
                    # BUG: Any trailing elements will be incorrectly offset, so won't work with finite length stuff
                    self.assign_target(elt, elt_type)
        elif isinstance(target, ast.Subscript):
            original_value_type = self.visit(target.value)
            origin = self.identify_caller(target.value)
            original_indexing_type = self.visit(target.slice)
            original_type = original_value_type.index(original_indexing_type)
            if operation:
                new_target_type = apply_binary_operation(operation, original_type, target_type)
                if isinstance(new_target_type, ImpossibleType):
                    self._issue(incompatible_types(self.locate(), operation, original_type, target_type, report=self.report))
            else:
                new_target_type = target_type
            original_type.set_index(original_indexing_type, new_target_type)
            if origin:
                origin_type = self.load_variable(origin)
                self.store_variable(origin, origin_type.type)
        elif isinstance(target, ast.Attribute):
            original_type = self.visit(target.value)
            origin = self.identify_caller(target.value)
            if operation:
                new_target_type = apply_binary_operation(operation, original_type, target_type)
                if isinstance(new_target_type, ImpossibleType):
                    self._issue(incompatible_types(self.locate(), operation, original_type, target_type, report=self.report))
            else:
                new_target_type = target_type
            assigned_type = original_type.add_attr(target.attr, new_target_type)
            if isinstance(assigned_type, ImpossibleType):
                self._issue(attribute_type_change(self.locate(), target.attr, original_type, new_target_type, report=self.report))
            if origin:
                origin_type = self.load_variable(origin)
                if origin_type:
                    self.store_variable(origin, origin_type.type)

    def visit_AnnAssign(self, node):
        """

        Args:
            node (ast.AnnAssign):

        Returns:

        """
        # Name, Attribute, or SubScript
        target = node.target
        # Type
        annotation = node.annotation
        annotation_type = self.evaluate_type(annotation)
        was_class_attribute = False
        # Optional assigned value
        value = node.value
        # 0 or 1, with 1 indicating pure names (not expressions)
        simple = node.simple

        # If it's a class attribute, then build up the type!
        if simple:
            current_scope = self.scope_chain[0]
            if current_scope in self.class_scopes:
                self.class_scopes[current_scope].add_attr(target.id, annotation)
                was_class_attribute = True
        # TODO: Allow setting for optional type coercion, or throw error
        if value:
            self.visit(value)
            # self.assign_target(target, self.visit(value))
        # Make local variable either way
        self.assign_target(target, annotation_type, store_with_read=was_class_attribute)

    def visit_Assign(self, node):
        """
        Simple assignment statement:
        __targets__ = __value__

        Args:
            node (ast.Assign): An Assign node
        Returns:
            None
        """
        # Handle value
        value_type = self.visit(node.value)
        # Apply value to all targets
        for target in node.targets:
            self.assign_target(target, value_type)

    def visit_AugAssign(self, node):
        """

        Args:
            node (ast.AugAssign):

        Returns:

        """
        # Handle value
        right = self.visit(node.value)
        if isinstance(node.target, ast.Name):
            self.load_variable(self.identify_caller(node.target))
        self.assign_target(node.target, right, node.op)

    def visit_Attribute(self, node):
        """

        Args:
            node:

        Returns:

        """
        # Handle value
        value_type = self.visit(node.value)
        self.check_common_bad_lookups(value_type, node.attr, node.value)
        # Handle attr
        result = value_type.get_attr(node.attr)
        # Set up self if this was a function (because now it's a method!)
        # TODO: Handle static/class functions differently I guess?
        if isinstance(result, FunctionType):
            result = result.as_method(value_type)
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
        operation = node.op

        new_target_type = apply_binary_operation(operation, left, right)
        if isinstance(new_target_type, ImpossibleType):
            self._issue(incompatible_types(self.locate(), operation, left, right, report=self.report))
        return new_target_type

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
        values = [self.visit(value) for value in node.values]
        # Handle operation
        # Actually, the operations are always the same behavior!
        # Handle truthiness
        if self.get_setting('truthiness_returns_booleans'):
            return BoolType()
        elif not values:
            return ImpossibleType()
        # All same type? Then return the first one!
        elif all(is_subtype(values[0], other) for other in values[1:]):
            return values[0]
        # Oh no, type union is necessary!
        else:
            return TypeUnion(values)

    def load_root_variable(self, node, position=None):
        root_name = self.identify_caller(node)
        if root_name is not None:
            variable = self.find_variable_scope(root_name)
            if variable.exists:
                return variable.state
        return None

    def visit_Call(self, node):
        # Handle func part
        function_type = self.visit(node.func)
        # TODO: Need to grab the actual type in some situations
        original_callee = self.load_root_variable(node)

        # Handle args
        arguments = [self.visit(arg) for arg in node.args] if node.args else []
        keywords = [(kwarg.arg, self.visit(kwarg.value))
                    for kwarg in node.keywords] if node.keywords else {}

        # Check special common mistakes

        if isinstance(function_type, BuiltinConstructorType):
            constructor = function_type.definition
            return constructor(self, function_type, original_callee,
                               arguments, keywords, self.locate())
        if isinstance(function_type, FunctionType):
            # Test if we have called this definition before
            if function_type.definition not in self.definition_chain:
                self.definition_chain.append(function_type.definition)
                # Function invocation
                result = function_type.definition(self, function_type, original_callee,
                                                  arguments, keywords, self.locate())
                self.definition_chain.pop()
                return result
            else:
                self._issue(recursive_call(self.locate(), original_callee, report=self.report))
        elif isinstance(function_type, ClassType):
            constructor = function_type.get_constructor().definition
            self.definition_chain.append(constructor)
            new_instance = constructor(self, constructor, original_callee, arguments, keywords, self.locate())
            self.definition_chain.pop()
            if '__init__' in function_type.fields:
                initializer = function_type.fields['__init__'].as_method(new_instance)
                if isinstance(initializer, FunctionType):
                    self.definition_chain.append(initializer)
                    initializer.definition(self, initializer, new_instance, [new_instance] + arguments, keywords, self.locate())
                    self.definition_chain.pop()
            return new_instance
        elif isinstance(function_type, (IntType, FloatType, NumType, ListType,
                                        DictType, SetType, TupleType, InstanceType,
                                        StrType, BoolType, NoneType, LiteralValue)):
            if original_callee is None:
                self._issue(not_a_function(self.locate(), "a value", function_type, report=self.report))
            else:
                self._issue(not_a_function(self.locate(), original_callee.name, function_type, report=self.report))
            return ImpossibleType()
        return AnyType()

    def visit_ClassDef(self, node):
        """

        Args:
            node:
        """
        class_name = node.name
        parents = [self.visit(base) for base in node.bases]
        new_class_type = ClassType(class_name, {}, parents)
        self.store_variable(class_name, new_class_type)
        definitions_scope = self.scope_chain[:]
        class_scope = NewScope(self, definitions_scope, class_type=new_class_type)
        # TODO: Handle metaclass... somehow?
        #self._visit_nodes(node.keywords)
        with class_scope:
            self._visit_nodes(node.body)
        new_class_type = self.apply_decorators(class_name, new_class_type, node.decorator_list)
        return new_class_type

    def apply_decorators(self, new_name, new_type, decorators):
        for decorator in reversed(decorators):
            old_type = self.load_variable(new_name)
            decorator_type = self.visit(decorator)
            original_callee = self.load_root_variable(decorator)
            new_type = decorator_type.definition(self, decorator_type, original_callee,
                                                 [new_type], {}, self.locate())
            self.store_variable(new_name, new_type)
        return new_type

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
                if type(right) in left.orderable:
                    continue
            elif isinstance(op, (ast.In, ast.NotIn)):
                if right.allows_membership(left):
                    continue
            self._issue(incompatible_types(self.locate(), op, left, right, report=self.report))
        return BoolType()

    def visit_comprehension(self, node):
        """

        Args:
            node:
        """
        self.fill_in_location(node, self.node_chain[-2])
        self._visit_collection_loop(node)
        # Handle ifs, unless they're blank (None in Skulpt :)
        if node.ifs:
            self.visit_statements(node.ifs)

    def fill_in_location(self, node, source_node):
        node.lineno = source_node.lineno
        node.col_offset = source_node.col_offset
        if IS_AT_LEAST_PYTHON_38:
            node.end_lineno = source_node.end_lineno
            node.end_col_offset = source_node.end_col_offset
        else:
            node.end_lineno = source_node.lineno
            node.end_col_offset = source_node.col_offset

    def visit_Dict(self, node):
        """
        Three types of dictionaries
        - empty
        - uniform type
        - record
        TODO: Handle records appropriately
        """
        items = [(self.visit(key), self.visit(value))
                 for key, value in zip(node.keys, node.values) if key is not None]
        # Unpack starred dictionaries
        for key, value in zip(node.keys, node.values):
            if key is None:
                value_type = self.visit(value)
                if isinstance(value_type, DictType):
                    items.extend([
                        (k, v) for k, v in value_type.element_types
                    ])
        # Empty dictionary
        if not items:
            return DictType([])
        # All literal keys
        if all(isinstance(k, LiteralValue) for k, _ in items):
            return DictType([(k, v) for k, v in items])
        # Find if all matched type
        first_key = widest_type([key for key, value in items])
        first_value = widest_type([value for key, value in items])
        if first_key is not None and first_value is not None:
            return DictType([(first_key, first_value)])
        else:
            # Resort to just matching the types?
            return DictType([(k, v) for k, v in items])

    def visit_DictComp(self, node):
        """

        Args:
            node:

        Returns:

        """
        generator_scope = NewScope(self, self.scope_chain[:])
        with generator_scope:
            self._visit_nodes(node.generators)
            keys = self.visit(node.key)
            values = self.visit(node.value)
            return DictType([(keys, values)])

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

    def visit_For(self, node):
        """

        Args:
            node:
        """
        was_empty = self._visit_collection_loop(node)
        # Handle the bodies
        # if not was_empty:
        # this_path_id = self.path_chain[0]
        # non_empty_path = NewPath(self, this_path_id, "f")
        # with non_empty_path:
        self.visit_statements(node.body)
        self.visit_statements(node.orelse)

    def visit_FunctionDef(self, node):
        """

        Args:
            node:

        Returns:

        """
        function_name = node.name
        position = self.locate()
        definitions_scope = self.scope_chain[:]
        definition = self.make_function(function_name, definitions_scope, position, node)
        function = FunctionType(function_name, definition=definition)
        self.store_variable(function_name, function)

        if len(self.node_chain) > 2:
            self._issue(nested_function_definition(self.locate(), function_name))

        return self.apply_decorators(function_name, function, node.decorator_list)

    def make_function(self, function_name, definitions_scope, position, node):
        is_lambda = function_name is None

        class SkipType:
            pass
        # Pull apart args into a coherent set of data PRIOR to execution
        args = node.args
        pos_parameters = args.posonlyargs + args.args if IS_AT_LEAST_PYTHON_38 else args.args
        none_padding = [SkipType] * (len(pos_parameters) - len(args.defaults))
        pos_defaults = none_padding + [self.visit(d) for d in args.defaults]
        kwarg_parameter = args.kwarg
        vararg_parameter = args.vararg

        # TODO: Finish kwargs
        named_parameters = args.kwonlyargs
        named_defaults = [self.visit(d) if d is not None else AnyType() for d in args.kw_defaults]
        expected_returns = self.evaluate_type(node.returns) if not is_lambda and node.returns else None

        def definition(tifa, function, callee_name, arguments, named_arguments, call_position):
            function_scope = NewScope(self, definitions_scope)
            with function_scope:
                # Process arguments
                if len(arguments) + len(named_arguments) != len(pos_parameters) and not vararg_parameter:
                    self._issue(incorrect_arity(self.locate(), function_name,
                                                len(pos_parameters), len(arguments), report=self.report))
                for parameter, default, argument in zip(pos_parameters, pos_defaults, arguments):
                    parameter_name = parameter.arg
                    if parameter.annotation:
                        annotation = self.evaluate_type(parameter.annotation)
                        if is_subtype(argument, annotation):
                            specify_subtype(annotation, argument)
                        else:
                            self._issue(parameter_type_mismatch(self.locate(), parameter_name,
                                                                annotation, argument))
                    elif default is not SkipType:
                        if is_subtype(argument, default):
                            specify_subtype(default, argument)
                        else:
                            self._issue(parameter_type_mismatch(self.locate(), parameter_name,
                                                                default, argument))
                    if argument is not None:
                        argument_type = argument.clone_mutably()
                        self.create_variable(parameter_name, argument_type, position)
                # Too many arguments
                if len(pos_parameters) < len(arguments):
                    if vararg_parameter:
                        the_rest = arguments[len(pos_parameters):]
                        self.create_variable(vararg_parameter.arg, TupleType(the_rest), position)
                # Not enough arguments
                if len(pos_parameters) > len(arguments):
                    for parameter in pos_parameters[len(arguments):]:
                        if parameter.annotation:
                            annotation = self.evaluate_type(parameter.annotation)
                        else:
                            annotation = AnyType()
                        self.create_variable(parameter.arg, annotation, position)
                if is_lambda:
                    return self.visit(node.body)

                self.visit_statements(node.body)
                return_state = self.find_variable_scope("*return")
                return_value = NoneType()
                # TODO: Figure out if we are not returning something when we should
                # If the pseudo variable exists, we load it and get its type
                if return_state.exists and return_state.in_scope:
                    return_state = self.load_variable("*return", call_position)
                    return_value = return_state.type
                    if expected_returns:
                        if not is_subtype(return_value, expected_returns):
                            self._issue(multiple_return_types(return_state.position,
                                                              expected_returns.singular_name,
                                                              return_value.singular_name,
                                                              report=self.report))
            return return_value
        return definition

    def evaluate_type(self, node):
        string_literal = False
        if isinstance(node, ast.Str):
            string_literal = node.s
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            string_literal = node.value
        if string_literal is not False:
            if self.get_setting('evaluate_string_literal_types'):
                # TODO: Handle string literal types properly!
                pass
            else:
                return LiteralStr(string_literal)
        elif isinstance(node, ast.List):
            if node.elts:
                return ListType(False, self.evaluate_type(node.elts[0]))
            else:
                return ListType(True)
        elif isinstance(node, ast.Set) and node.elts:
            return TypeUnion([self.evaluate_type(e) for e in node.elts])
        elif isinstance(node, ast.Tuple) and node.elts:
            return TupleType([self.evaluate_type(e) for e in node.elts])
        elif isinstance(node, ast.Dict):
            if node.keys and node.values:
                return DictType([(self.evaluate_type(k), self.evaluate_type(v))
                                 for k, v in zip(node.keys, node.values)])
            else:
                return DictType([])
        else:
            evaluated = self.visit(node)
            return evaluated.as_type(self, self.locate(node))

    def visit_GeneratorExp(self, node):
        """

        Args:
            node:

        Returns:

        """
        generator_scope = NewScope(self, self.scope_chain[:])
        with generator_scope:
            self._visit_nodes(node.generators)
            return GeneratorType(False, self.visit(node.elt))

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

        if is_subtype(body, orelse):
            return body

        # TODO: Union type?
        return TypeUnion([body, orelse])

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
            if alias.name == '*':
                module_type = self.load_module(node.module)
                for field, value in module_type.fields.items():
                    self.store_read_variable(field, value)
            else:
                if node.module is None:
                    asname = alias.asname or alias.name
                    module_type = self.load_module(alias.name)
                else:
                    module_name = node.module
                    asname = alias.asname or alias.name
                    module_type = self.load_module(module_name)
                name_type = module_type.get_attr(alias.name)
                self.store_variable(asname, name_type)

    def visit_Lambda(self, node):
        """

        Args:
            node:

        Returns:

        """
        position = self.locate()
        definitions_scope = self.scope_chain[:]
        definition = self.make_function(None, definitions_scope, position, node)
        return FunctionType("*lambda", definition=definition)

    def visit_List(self, node):
        """

        Args:
            node:

        Returns:

        """
        if not node.elts:
            return ListType(True)

        # All literal keys
        elements = [self.visit(v) for v in node.elts]
        if all(isinstance(v, LiteralValue) for v in elements):
            # TODO: Allow type union instead?
            return ListType(False, elements[0].promote())
        # Find if all matched type
        first_value = widest_type(elements)
        if first_value is not None:
            return ListType(False, first_value)
        else:
            # Resort to just matching the types?
            return ListType(False, TypeUnion(elements))

    def visit_ListComp(self, node):
        """

        Args:
            node:

        Returns:

        """
        # TODO: Handle comprehension scope
        generator_scope = NewScope(self, self.scope_chain[:])
        with generator_scope:
            self._visit_nodes(node.generators)
            return ListType(False, self.visit(node.elt))

    def visit_NameConstant(self, node):
        """

        Args:
            node:

        Returns:

        """
        value = node.value
        if isinstance(value, bool):
            return LiteralBool(value)
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
                return LiteralBool(name == "True")
            elif name == "None":
                return NoneType()
            else:
                variable = self.find_variable_scope(name)
                builtin = get_builtin_name(name)
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
                return AnyType()

    def visit_Num(self, node):
        """

        Args:
            node:

        Returns:

        """
        return LiteralInt(node.n) if isinstance(node.n, int) else LiteralFloat(node.n)

    def visit_Constant(self, node) -> Type:
        """ Handle new 3.8's Constant node """
        return get_pedal_type_from_value(node.value, self.evaluate_type)

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
        if not node.elts:
            return SetType(True)

        # All literal keys
        elements = [self.visit(v) for v in node.elts]
        if all(isinstance(v, LiteralValue) for v in elements):
            # TODO: Allow type union instead?
            return SetType(False, elements[0].promote())
        # Find if all matched type
        first_value = widest_type(elements)
        if first_value is not None:
            return SetType(False, first_value)
        else:
            # Resort to just matching the types?
            return SetType(False, TypeUnion(elements))

    def visit_SetComp(self, node):
        """

        Args:
            node:

        Returns:

        """
        # TODO: Handle comprehension scope
        generator_scope = NewScope(self, self.scope_chain[:])
        with generator_scope:
            self._visit_nodes(node.generators)
            return SetType(False, self.visit(node.elt))

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
        return LiteralStr(node.s)

    def visit_JoinedStr(self, node):
        values = [self.visit(expr) for expr in node.values]
        # The result will be all StrType
        return StrType(is_empty=all(isinstance(n, (StrType, LiteralStr)) and n.is_empty
                                    for n in values))

    def visit_FormattedValue(self, node):
        value = self.visit(node.value)
        if isinstance(value, StrType):
            return value
        else:
            return StrType(is_empty=False)

    def visit_Subscript(self, node):
        """

        Args:
            node:

        Returns:

        """
        # Handle value
        value_type = self.visit(node.value)
        slice_type = self.visit(node.slice)
        result = value_type.index(slice_type)
        if isinstance(result, ImpossibleType):
            self._issue(invalid_indexing(self.locate(), value_type, slice_type))
        if isinstance(node.slice, ast.Slice):
            return value_type.shallow_clone()
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

    def visit_Index(self, node):
        return self.visit(node.value)

    def visit_ExtSlice(self, node):
        return TupleType([self.visit(d) for d in node.dims])

    def visit_Starred(self, node):
        return self.visit(node.value).break_apart()

    def visit_Tuple(self, node) -> TupleType:
        # Fun fact, it's impossible to make a literal empty set
        if not node.elts:
            return TupleType(True)

        # All literal keys
        return TupleType([self.visit(v) for v in node.elts])

    def visit_UnaryOp(self, node):
        """

        Args:
            node:

        Returns:

        """
        # Handle operand
        operand_type = self.visit(node.operand)
        return apply_unary_operation(node.op, operand_type)

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
            if item.optional_vars is not None:
                self.assign_target(item.optional_vars, type_value)
        # Handle the bodies
        self.visit_statements(node.body)

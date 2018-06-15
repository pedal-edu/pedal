'''
Python Type Inferencer and Flow Analyzer (TIFA)
 
TIFA uses a number of simplifications of the Python language.
  * Variables cannot change type
  * Variables cannot be deleted
  * Complex types have to be homogenous
  * No introspection or reflective characteristics
  * No dunder methods
  * No closures (maybe?)
  * You cannot write a variable out of scope
  * You cannot read a mutable variable out of scope
  * No multiple inheritance
  
Additionally, it reads the following as issues:
  * Cannot read a variable without having first written to it.
  * Cannot rewrite a variable unless it has been read.
'''

import ast

class Type:
    '''
    Parent class for all other types, used to provide a common interface.
    '''
    def clone(self):
        return self.__class__()
    def index(self, i):
        return self.clone()

class UnknownType(Type):
    '''
    A special type used to indicate an unknowable type.
    '''

class RecursedType(Type):
    '''
    A special type used as a placeholder for the result of a
    recursive call that we have already process. This type will
    be dominated by any actual types, but will not cause an issue.
    '''

class TupleType(Type):
    '''
    '''
    def __init__(self, subtypes=None):
        if subtypes is None:
            subtypes = []
        self.subtypes = subtypes
    def index(self, i):
        if isinstance(i, LiteralNum):
            return self.subtypes[i.value].clone()
        else:
            return self.subtypes[i].clone()
    def clone(self):
        return TupleType([t.clone() for t in self.subtypes])

class ListType(Type):
    def __init__(self, subtype=None, empty=True):
        if subtype is None:
            subtype = UnknownType()
        self.subtype = subtype
        self.empty = empty
    def index(self, i):
        return self.subtype.clone()
    def clone(self):
        return ListType(self.subtype.clone(), self.empty)

class StrType(Type):
    def index(self, i):
        return StrType()
class FileType(Type):
    def index(self, i):
        return StrType()
    
class DictType(Type):
    def __init__(self, empty=False, literals=None, keys=None, values=None):
        self.empty = empty
        self.literals = literals
        self.values = values
        self.keys = keys
    def index(self, i):
        if self.literals is not None:
            for literal, value in zip(self.literals, self.values):
                if Tifa.are_literals_equal(literal, i):
                    return value.clone()
            return UnknownType()
        else:
            return self.keys.clone()

class NumType(Type):
    pass
    
class NoneType(Type):
    pass
    
class BoolType(Type):
    pass

class ModuleType(Type):
    pass

class SetType(ListType):
    pass

class GeneratorType(ListType):
    pass
    
def are_types_equal(left, right):
    '''
    Determine if two types are equal.
    '''
    if left is None or right is None:
        return False
    elif isinstance(left, UnknownType) or isinstance(right, UnknownType):
        return False
    elif type(left) != type(right):
        return False
    elif isinstance(left, (GeneratorType, ListType)):
        if left.empty or right.empty:
            return True
        else:
            return are_types_equal(left.subtype, right.subtype)
    elif isinstance(left, TupleType):
        if left.empty or right.empty:
            return True
        elif len(left.subtypes) != len(right.subtypes):
            return False
        else:
            for l, r in zip(left.subtypes, right.subtypes):
                if not are_types_equal(l, r):
                    return False
            return True
    elif isinstance(left, DictType):
        if left.empty or right.empty:
            return True
        elif left.literals is not None and right.literals is not None:
            if len(left.literals) != len(right.literals):
                return False
            else:
                for l, r in zip(left.literals, right.literals):
                    if not are_types_equal(l, r):
                        return False
                for l, r in zip(left.values, right.values):
                    if not are_types_equal(l, r):
                        return False
                return True
        elif left.literals is not None or right.literals is not None:
            return False
        else:
            keys_equal = are_types_equal(left.keys, right.keys)
            values_equal = are_types_equal(left.values, right.values)
            return keys_equal and values_equal
    else:
        return True

class LiteralValue:
    '''
    A special literal representation of a value, used to represent access on
    certain container types.
    '''
    pass
    
class LiteralNum(LiteralValue):
    '''
    Used to capture indexes of containers.
    '''
    def __init__(self, value):
        self.value = value
        
class Identifier:
    '''
    A representation of an Identifier, encapsulating its current level of
    existence, scope and State.
    
    Attributes:
        exists (bool): Whether or not the variable actually is defined anywhere.
                       It is possible that a variable was retrieved that does
                       not actually exist yet, which indicates it might need to
                       be created.
        in_scope (bool): Whether or not the variable exists in the current
                         scope. Used to detect the presence of certain kinds
                         of errors where the user is using a variable from
                         a different scope.
        scoped_name (str): The fully qualified name of the variable, including
                           its scope chain.
        state (State): The current state of the variable.
    '''
    def __init__(self, exists, in_scope=False, scoped_name="UNKNOWN", state=""):
        self.exists = exists
        self.in_scope = in_scope
        self.scoped_name = scoped_name
        self.state = state
    
class State:
    '''
    A representation of a variable at a particular point in time of the program.
    
    Attributes:
        name (str): The name of the variable, without its scope chain
        trace (list of State): A recursive definition of previous States for
                               this State.
        type (Type): The current type of this variable.
        method (str): One of 'store', 'read', (TODO). Indicates the change that
                      occurred to this variable at this State.
        position (dict): A Position dictionary indicating where this State
                         change occurred in the source code.
        read (str): One of 'yes', 'no', or 'maybe'. Indicates if this variable
                    has been read since it was last changed. If merged from a
                    diverging path, it is possible that it was "maybe" read.
        set (str): One of 'yes', 'no', or 'maybe'. Indicates if this variable
                    has been set since it was last read. If merged from a 
                    diverging path, it is possible that it was "maybe" changed.
        over (str): One of 'yes', 'no', or 'maybe'. Indicates if this variable
                    has been overwritten since it was last set. If merged from a 
                    diverging path, it is possible that it was "maybe" changed.
        over_position (dict): A Position indicating where the State was
                              previously set versus when it was overwritten.
        
    '''
    def __init__(self, name, trace, type, method, position, 
                 read='maybe', set='maybe', over='maybe', over_position=None):
        self.name = name
        self.trace = trace
        self.type = type
        self.method = method
        self.position = position
        self.over_position = over_position
        self.read = read
        self.set = set
        self.over = over
    
    def copy(self, method, position):
        '''
        Make a copy of this State, copying this state into the new State's trace
        '''
        return State(self.name, [self], self.type, method, position,
                     state.read, state.set, state.over, state.over_position)

    def __str__(self):
        '''
        Create a string representation of this State.
        '''
        return self.method+"("+"|".join((self.read, self.set, self.over))+")"
    def __repr__(self):
        '''
        Create a string representation of this State.
        '''
        return str(self)
                     
class Tifa(ast.NodeVisitor):
    @staticmethod
    def _error_report(error):
        '''
        Return a new unsuccessful report with an error present.
        '''
        return {"success": False, 
                "error": error,
                "issues": {},
                "variables": {}}
    
    @staticmethod
    def _initialize_report():
        '''
        Return a successful report with possible set of issues.
        '''
        return {"success": True,
                "variables": {},
                "issues": {
                    "Parser Failure": [], # Complete failure to parse the code
                    "Unconnected blocks": [], # Any names with ____
                    "Empty Body": [], # Any use of pass on its own
                    "Malformed Conditional": [], # An if/else with empty else or if
                    "Unnecessary Pass": [], # Any use of pass
                    "Unread variables": [], # A variable was not read after it was defined
                    "Undefined variables": [], # A variable was read before it was defined
                    "Possibly undefined variables": [], # A variable was read but was not defined in every branch
                    "Overwritten variables": [], # A written variable was written to again before being read
                    "Append to non-list": [], # Attempted to use the append method on a non-list
                    "Used iteration list": [], # 
                    "Unused iteration variable": [], # 
                    "Non-list iterations": [], # 
                    "Empty iterations": [], # 
                    "Type changes": [], # 
                    "Iteration variable is iteration list": [], # 
                    "Unknown functions": [], # 
                    "Not a function": [], # Attempt to call non-function as function
                    "Recursive Call": [],
                    "Incorrect Arity": [],
                    "Action after return": [],
                    "Incompatible types": [], # 
                    "Return outside function": [], # 
                    "Read out of scope": [], # 
                    "Write out of scope": [], # Attempted to modify a variable in a higher scope
                    "Aliased built-in": [], # 
                    "Method not in Type": [], # A method was used that didn't exist for that type
                    "Submodule not found": [],
                    "Module not found": []
                }
        }
    
    def report_issue(self, issue, data):
        '''
        Report the given issue with associated metadata, including the position
        if not explicitly included.
        '''
        if 'position' not in data:
            data['position'] = self.locate()
        self.report.issues[issue].append(data)
        
    def locate(self):
        '''
        Return a dictionary representing the current location within the
        AST.
        
        Returns:
            Position dict: A dictionary with the fields 'column' and 'line',
                           indicating the current position in the source code.
        '''
        node = self.node_chain[-1]
        return {'column': node.col_offset, 'line': node.lineno}
                
    def process_code(self, code, filename="__main__"):
        '''
        Processes the AST of the given source code to generate a report.
        
        Args:
            code (str): The Python source code
            filename (str): The filename of the source code (defaults to __main__)
        Returns: 
            Report: The successful or successful report object
        '''
        # Code
        self.source = code.split("\n") if code else []
        filename = filename
        
        # Attempt parsing - might fail!
        try:
            ast_tree = ast.parse(code, filename)
            return self.process_ast(ast_tree)
        except Exception as error:
            self.report = Tifa._error_report(error)
            raise error
            return self.report;
    
    def process_ast(self, ast_tree):
        '''
        Given an AST, actually performs the type and flow analyses to return a 
        report.
        
        Args:
            ast (Ast): The AST object
        Returns:
            Report: The final report object created (also available as a field).
        '''
        self._reset()
        # Initialize a new, empty report
        self.report = Tifa._initialize_report()
        # Traverse every node
        self.visit(ast_tree);
        
        # Check afterwards
        self.report['variables'] = self.name_map
        self._finish_scope()
        
        # Collect top level variables
        self._collect_top_level_varaibles()
        #print(self.report['variables'])
        
        return self.report
    
    def _collect_top_level_varaibles(self):
        '''
        Walk through the variables and add any at the top level to the
        top_level_variables field of the report.
        '''
        self.report['top_level_variables'] = {}
        main_path_vars = self.name_map[self.path_chain[0]]
        for full_name in main_path_vars:
            split_name = full_name.split("/")
            if len(split_name) == 2 and split_name[0] == self.scope_chain[0]:
                self.report.top_level_variables[split_name[1]] = main_path_vars[fullName]
    
    def _reset(self):
        '''
        Reinitialize fields for maintaining the system
        '''
        # Unique Global IDs
        self.path_id = 0;
        self.scope_id = 0;
        self.ast_id = 0;
        
        # Human readable names
        self.path_names = ['*Module'];
        self.scope_names = ['*Module'];
        self.node_chain = [];
        
        # Complete record of all Names
        self.scope_chain = [self.scope_id]
        self.path_chain = [self.path_id]
        self.name_map = {}
        self.name_map[self.path_id] = {}
        self.definition_chain = []
        self.path_parents = {}
        
    def find_variable_scope(self, name):
        '''
        Walk through this scope and all enclosing scopes, finding the relevant
        identifier given by `name`.
        
        Returns:
            Identifier: An Identifier for the variable, which could potentially
                        not exist.
        '''
        for scope_index, scope in enumerate(self.scope_chain):
            for path_id in self.path_chain:
                path = self.name_map[path_id]
                full_name = "/".join(map(str, self.scope_chain[:scope_index]))+"/"+name
                if full_name in path:
                    is_root_scope = (scope_index==0)
                    return Identifier(True, is_root_scope, 
                                      full_name, path[full_name])
                        
        return Identifier(False)
        
    def _finish_scope(self):
        '''
        Walk through all the variables present in this scope and ensure that
        they have been read and not overwritten.
        '''
        path_id = self.path_chain[0];
        for name in self.name_map[path_id]:
            if Tifa.sameScope(name, self.scope_chain):
                state = self.name_map[path_id][name]
                if state.over == 'yes':
                    position = state.over_position
                    self.report_issue('Overwritten variables', 
                                     {'name': state.name, 'position': position})
                if state.read == 'no':
                    self.report_issue('Unread variables', 
                                     {'name': state.name, 'type': state.type})
        
    def visit(self, node):
        '''
        Process this node by calling its appropriate visit_*
        
        Args:
            node (AST): The node to visit
        Returns:
            Type: The type calculated during the visit.
        '''
        # Start processing the node
        self.node_chain.append(node)
        self.ast_id += 1
        
        # Actions after return?
        if len(self.scope_chain) > 1:
            return_state = self.find_variable_scope("*return")
            if return_state.exists and return_state.in_scope:
                if return_state.state.set == "yes":
                    self.report_issue("Action after return")
        
        # No? All good, let's enter the node
        result = super().visit(node)
        
        # Pop the node out of the chain
        self.ast_id -= 1
        self.node_chain.pop()
        
        # If a node failed to return something, return the UNKNOWN TYPE
        if result == None:
            return UnknownType()
        else:
            return result
            
    def _visit_nodes(self, nodes):
        '''
        Visit all the nodes in the given list.
        
        Args:
            nodes (list): A list of values, of which any AST nodes will be
                          visited.
        '''
        for node in nodes:
            if isinstance(node, ast.AST):
                self.visit(node)
                
    def walk_targets(self, targets, type, walker):
        '''
        Iterate through the targets and call the given function on each one.
        
        Args:
            targets (list of Ast nodes): A list of potential targets to be
                                         traversed.
            type (Type): The given type to be unraveled and applied to the
                         targets.
            walker (Ast Node, Type -> None): A function that will process
                                             each target and unravel the type.
        '''
        for target in targets:
            walker(target, type)
            
    def visit_Assign(self, node):
        '''
        Simple assignment statement:
        __targets__ = __value__
        
        Args:
            node (AST): An Assign node
        Returns:
            None
        '''
        # Handle value
        value_type = self.visit(node.value);
        # Handle targets
        self._visit_nodes(node.targets);
        
        # TODO: Properly handle assignments with subscripts
        def action(target, type):
            if isinstance(target, ast.Name):
                self.store_variable(target.id, type)
            elif isinstance(target, (ast.Tuple, ast.List)):
                for i, elt in enumerate(target.elts):
                    eltType = Tifa.index_sequence_type(type, LiteralNum(i))
                    action(elt, eltType)
            elif isinstance(target, ast.Subscript):
                pass
                # TODO: Handle minor type changes (e.g., appending to an inner list)
        self.walk_targets(node.targets, value_type, action)
        
    def _scope_chain_str(self):
        '''
        Convert the current scope chain to a string representation (divided 
        by "/").
        
        Returns:
            str: String representation of the scope chain.
        '''
        return "/".join(map(str, self.scope_chain))
        
    def store_variable(self, name, type):
        '''
        Update the variable with the given name to now have the new type.
        
        Args:
            name (str): The unqualified name of the variable. The variable will
                        be assumed to be in the current scope.
            type (Type): The new type of this variable.
        Returns:
            State: The new state of the variable.
        '''
        full_name = self._scope_chain_str() + "/" + name
        current_path = self.path_chain[0]
        variable = self.find_variable_scope(name)
        if not variable.exists:
            # Create a new instance of the variable on the current path
            new_state = State(name, [], type, 'store', self.locate(), 
                              read='no', set='yes', over='no')
            self.name_map[current_path][full_name] = new_state
        else:
            new_state = self.trace_state(variable.state, "store")
            if not variable.in_scope:
                self.report_issue("Write out of scope", {'name': name})
            # Type change?
            if not are_types_equal(type, variable.state.type):
                self.report_issue("Type changes", 
                                 {'name': name, 'old': variable.state.type, 
                                  'new': type})
            new_state.type = type
            # Overwritten?
            if variable.state.set == 'yes' and variable.state.read == 'no':
                new_state.over_position = position
                new_state.over = 'yes'
            else:
                new_state.set = 'yes'
                new_state.read = 'no'
            self.name_map[current_path][full_name] = new_state
        return new_state
    
    @staticmethod
    def index_sequence_type(type, i=0):
        return type.index(i)
    
    def trace_state(self, state, method):
        return state.copy(method, self.locate())
    
    @staticmethod
    def sameScope(full_name, scope_chain):
        # Get this entity's full scope chain
        name_scopes = full_name.split("/")[:-1]
        # against the reverse scope chain
        checking_scopes = scope_chain[::-1]
        return name_scopes == checking_scopes
    
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
    pass

class UnknownType(Type):
    '''
    A special type used to indicate an unknowable type.
    '''
    pass

class RecursedType(Type):
    '''
    A special type used as a placeholder for the result of a
    recursive call that we have already process. This type will
    be dominated by any actual types, but will not cause an issue.
    '''
    pass

class LiteralValue:
    pass
    
class LiteralNum(LiteralValue):
    def __init__(self, value):
        self.value = value
        
class Identifier:
    def __init__(self, exists, in_scope=False, scoped_name="UNKNOWN", state=""):
        self.exists = exists
        self.in_scope = in_scope
        self.scoped_name = scoped_name
        self.state = state
    
class State:
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
        return State(self.name, [self], self.type, method, position,
                     state.read, state.set, state.over, state.over_position)

    def __str__(self):
        return self.method+"("+"|".join((self.read, self.set, self.over))+")"
    def __repr__(self):
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
        if 'position' not in data:
            data['position'] = self.locate()
        self.report.issues[issue].append(data)
        
    def locate(self):
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
        for j, scope in enumerate(self.scope_chain):
            for path_id in self.path_chain:
                path = self.name_map[path_id]
                full_name = "/".join(map(str, self.scope_chain[:j]))+"/"+name
                if full_name in path:
                    return Identifier(True, j==0, full_name, path[full_name])
                        
        return Identifier(False)
        
    def _finish_scope(self):
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
        for node in nodes:
            if isinstance(node, ast.AST):
                self.visit(node)
                
    def walk_targets(self, targets, type, walker):
        for target in targets:
            walker(target, type)
            
    def visit_Assign(self, node):
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
        return "/".join(map(str, self.scope_chain))
        
    def store_variable(self, name, type):
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
            if not Tifa.are_types_equal(type, variable.state.type):
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
        return new_state;
    
    @staticmethod
    def index_sequence_type(type, i=0):
        #TODO
        pass
    
    def trace_state(self, state, method):
        return state.copy(method, self.locate())
    
    @staticmethod
    def are_types_equal(left, right):
        #TODO
        pass
    
    @staticmethod
    def sameScope(full_name, scope_chain):
        # Get this entity's full scope chain
        name_scopes = full_name.split("/")[:-1]
        # against the reverse scope chain
        checking_scopes = scope_chain[::-1]
        return name_scopes == checking_scopes
    
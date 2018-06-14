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
    pass

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
        self.report.issues[issue].append(data)
                
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
            ast_tree = ast.parse(filename, code)
            return self.process_ast(ast_tree)
        except Exception as error:
            self.report = Tifa._error_report(error)
            return self.report;
    
    def process_ast(self, ast):
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
        self.visit(ast);
        
        # Check afterwards
        self.report['variables'] = self.name_map
        self._finish_scope()
        
        # Collect top level variables
        self.report['top_level_variables'] = {}
        main_path_vars = self.name_map[self.path_chain[0]]
        for full_name in main_path_vars:
            split_name = full_name.split("/")
            if split_name.length == 2 and split_name[0] == self.scope_chain[0]:
                self.report.top_level_variables[split_name[1]] = main_path_vars[fullName]
        
        return self.report
    
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
        self.ast_names = [];
        
        # Complete record of all Names
        self.scope_chain = [self.scope_id]
        self.path_chain = [self.path_id]
        self.name_map = {}
        self.name_map[self.path_id] = {}
        self.definition_chain = []
        self.path_parents = {}
        
    def visit(self, node):
        '''
        '''
        # Actions after return?
        if len(self.scope_chain) > 1:
            return_state = self.find_variable_scope("*return")
            if return_state.exists and return_state.in_scope:
                if return_state.state.set == "yes":
                    self.report_issue("Action after return", {"position": Tifa.locate(node)})
        
        # No? All good, let's enter the node
        self.ast_names.append(node.__class__.__name__)
        self.ast_id += 1
        result = super().visit(node)
        self.ast_id -= 1
        self.ast_names.pop()
        
        # If a node failed to return something, return the UNKNOWN TYPE
        if result == None:
            return UnknownType()
        else:
            return result
        
    @staticmethod
    def locate(node):
        return {"column": node.col_offset, "line": node.lineno}
    
    def find_variable_scope(self, name):
        pass
        
    def _finish_scope(self):
        pass
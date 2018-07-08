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
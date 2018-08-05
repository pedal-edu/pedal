
def check_trace(state):
        past_types = [state.type]
        for past_state in state.trace:
            past_types.extend(check_trace(past_state))
        return past_types

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
                     self.read, self.set, self.over, self.over_position)

    def __str__(self):
        '''
        Create a string representation of this State.
        '''
        return "{method}(r:{read},s:{set},o:{over},{type})".format(
            method=self.method,
            read=self.read[0],
            set=self.set[0],
            over=self.over[0],
            type=self.type.__class__.__name__
        )
    def __repr__(self):
        '''
        Create a string representation of this State.
        '''
        return str(self)
    
    def was_type(self, a_type):
        '''
        Retrieve all the types that this variable took on over its entire
        trace.
        '''
        past_types = check_trace(self)
        return any(past_type.is_equal(a_type) for past_type in past_types)
    
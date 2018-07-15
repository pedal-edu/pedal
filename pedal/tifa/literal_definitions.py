

def are_literals_equal(first, second):
    if first is None or second is None:
        return False
    elif type(first) != type(second):
        return False
    else:
        if isinstance(first, LiteralTuple):
            if len(first.value) != len(second.value):
                return False
            for l, s in zip(first.value, second.value):
                if not are_literals_equal(l, s):
                    return False
            return True
        else:
            return first.value == second.value

class LiteralValue:
    '''
    A special literal representation of a value, used to represent access on
    certain container types.
    '''
    def __init__(self, value):
        self.value = value
    
class LiteralNum(LiteralValue):
    '''
    Used to capture indexes of containers.
    '''    
    def type(self):
        return NumType()

class LiteralBool(LiteralValue):
    def type(self):
        return BoolType()
        
class LiteralStr(LiteralValue):
    def type(self):
        return StrType()
        
class LiteralTuple(LiteralValue):
    def type(self):
        return TupleType(self.value)
        
class LiteralNone(LiteralValue):
    def type(self):
        return LiteralNone()

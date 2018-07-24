
class Feedback:
    def __init__(self, message, priority, line, namespace, value):
        pass
        
'''
What are these atomic things (X)?

Feedback: This is what is delivered to the student, not the raw thing that is
          stored internally.
Mistake/Issue: This is not accurate when we want to raise something positive, but
               might be accurate in describing the idea that something is worth
               reporting.
Complaint/Compliment: A nice dichotomy, but these seem more like subclasses
                      of a broader idea.
Explanation: This is more of a Why type of thing.

They have a `priority` indiciating their ordering
They have a namespace indicating what tool produced them
They have a weight indicating their value relative to other X
They have various messages that could be displayed

What:
When:
Where:
    Position
        Line
        Line and Colno
    Range
        Line/Colno + Line/Colno
        Line + Line
    Sequence of Range and Positions
How:
'''

class Report:
    
    def __init__(self):
        self.success = False
        self.compliments = []
        self.complaints = []
        self.suppressions = []
        self._results = {}

    def set_success(self):
        pass
        
    def compliment(self, message):
        pass
        
    def give_partial(self, value, message):
        pass
        
    def hide_correctness(self):
        pass
        
    def explain(self, message, priority, line):
        pass

    def gently(self, message, line):
        pass

    def suppress(self, type, subtype):
        pass
        
    def log(self, message):
        pass
        
    def debug(self, message):
        pass

    def __getitem__(self, key):
        return self._results[key]
    
    def __setitem__(self, key, value):
        self._results[key] = value
    
    def __contains__(self, key):
        return key in self._results
    
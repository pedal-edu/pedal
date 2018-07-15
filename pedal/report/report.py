
class Feedback:
    def __init__(self, message, priority, line, namespace, value):
        pass

class Report:
    
    def __init__(self):
        self.success = False
        self.compliments = []
        self.complaints = []

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
    

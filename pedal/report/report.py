from pedal.report.feedback import Feedback

__all__ = ['Report']

class Report:
    '''
    A class for storing Feedback generated by Tools, along with any auxiliary
    data that the Tool might want to provide for other tools.
    
    Attributes:
        feedback (list of Feedback): The raw feedback generated for this Report
                                     so far.
        suppressions (list of tuple(str, str)): The categories and labels that
                                                have been suppressed so far.
        _results (dict of str => any): Maps tool names to their data. The
                                       namespace for a tool can be used to
                                       store whatever they want, but will
                                       probably be in a dictionary itself.
    '''
    
    def __init__(self):
        self.clear()
    
    def clear(self):
        self.feedback = []
        self.suppressions = {}
        self._results = {}

    def set_success(self):
        self.feedback.append(Feedback('set_success', priority='positive',
                                      result=True))
        
    def give_partial(self, value, message=None):
        self.feedback.append(Feedback('give_partial', performance=value,
                                      priority='positive',
                                      mistakes=message))
        
    def hide_correctness(self):
        self.suppressions['success'] = []
        
    def explain(self, message, priority='medium', line=None):
        misconception = {'message': message}
        if line is not None:
            misconception['line'] = line
        self.feedback.append(Feedback('explain', priority=priority,
                                      category='instructor',
                                      misconceptions=misconception))

    def gently(self, message, line=None):
        self.explain(message, priority='student', line=line)
    
    def compliment(self, message, line=None):
        self.explain(message, priority='positive', line=line)
    
    def attach(self, label, **kwargs):
        self.feedback.append(Feedback(label, **kwargs))

    def suppress(self, category, label=True):
        category = category.lower()
        if isinstance(label, str):
            label = label.lower()
        if category not in self.suppressions:
            self.suppressions[category] = []
        self.suppressions[category].append(label)
        
    def log(self, message):
        pass
        
    def debug(self, message):
        pass

    def __getitem__(self, key):
        if key not in self._results:
            self._results[key] = {}
        return self._results[key]
    
    def __setitem__(self, key, value):
        self._results[key] = value
    
    def __contains__(self, key):
        return key in self._results

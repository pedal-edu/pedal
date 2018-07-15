from pedal.report.report import Report

_MAIN_REPORT = Report()

def set_success():
    _MAIN_REPORT.set_success()
    
def compliment(message):
    _MAIN_REPORT.compliment(message)
    
def give_partial(value, message):
    _MAIN_REPORT.give_partial(value, message)
    
def hide_correctness():
    _MAIN_REPORT.hide_correctness()
    
def explain(message, priority, line):
    _MAIN_REPORT.explain(message, priority, line)

def gently(message, line):
    _MAIN_REPORT.gently(message, line)

def suppress(type, subtype):
    _MAIN_REPORT.suppress(type, subtype)
    
def log(message):
    _MAIN_REPORT.log(message)
    
def debug(message):
    _MAIN_REPORT.debug(message)

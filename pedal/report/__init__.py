from pedal.report.report import Report

MAIN_REPORT = Report()

def set_success():
    MAIN_REPORT.set_success()
    
def compliment(message):
    MAIN_REPORT.compliment(message)
    
def give_partial(value, message):
    MAIN_REPORT.give_partial(value, message)
    
def hide_correctness():
    MAIN_REPORT.hide_correctness()
    
def explain(message, priority, line):
    MAIN_REPORT.explain(message, priority, line)

def gently(message, line):
    MAIN_REPORT.gently(message, line)

def suppress(type, subtype):
    MAIN_REPORT.suppress(type, subtype)
    
def log(message):
    MAIN_REPORT.log(message)
    
def debug(message):
    MAIN_REPORT.debug(message)

import pedal.report as report

def select(feedback_report=None):
    '''
    Args:
        reports (list of Report): A list of report objects to be traversed.
    
    Returns
        str: A string of HTML feedback to be delivered
    '''
    if feedback_report is None:
        feedback_report = report._MAIN_REPORT
    return feedback_report.complaints[0]
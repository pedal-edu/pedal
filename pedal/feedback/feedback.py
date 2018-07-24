import pedal.report as report

def select(report=None):
    '''
    Args:
        report (Report): The report object to resolve down
    
    Returns
        str: A string of HTML feedback to be delivered
    '''
    if report is None:
        report = report._MAIN_REPORT
    return report.feedback[0]

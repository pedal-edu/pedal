from pedal.report import MAIN_REPORT

def parse_component(component):
    if isinstance(component, str):
        return component
    elif isinstance(component, list):
        return '<br>\n'.join(parse_component(c) for c in component)
    elif isinstance(component, dict):
        if "html" in component:
            return component["html"]
        elif "message" in component:
            return component["message"]
        else:
            raise ValueError("Component has no message field: "+str(component))
    else:
        raise ValueError("Invalid component type: "+str(type(component)))

def resolve(report=None):
    '''
    Args:
        report (Report): The report object to resolve down. Defaults to the
                         global MAIN_REPORT
    
    Returns
        str: A string of HTML feedback to be delivered
    '''
    if report is None:
        report = MAIN_REPORT
    feedbacks = report.feedback
    success = False
    message = "No errors reported."
    for feedback in feedbacks[::-1]:
        if feedback.result is not None:
            success = success or feedback.result
        if feedback.mistakes is not None:
            message = parse_component(feedback.mistakes)
        if feedback.misconceptions is not None:
            message = parse_component(feedback.misconceptions)

    return success, message

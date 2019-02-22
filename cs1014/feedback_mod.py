from pedal.report.imperative import explain, gently


def gently_r(message, code, line=None, tldr="explain"):
    gently(message + "<br><br><i>({})<i></br></br>".format(code), line, label=tldr)
    return message


def explain_r(message, code, priority='medium', line=None, tldr="explain"):
    explain(message + "<br><br><i>({})<i></br></br>".format(code), priority, line, label=tldr)
    return message


def codify(code):
    return "<code>" + code + "</code>"

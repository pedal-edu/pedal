from pedal.mistakes.feedback_mod import *
from pedal.cait.cait_api import *


def unnecessary_cast(needed_casts):
    """

    Args:
        needed_casts: List of casts that are necessary to this problem

    Returns:

    """
    message = "Converting to {} is unnecessary in this problem"
    code = "ex_cast"
    tldr = "Unnecessary Conversion"

    known_casts = ["float", "int", "str"]
    matches = find_matches("_cast_(___)")
    for match in matches:
        user_cast = match["_cast_"].id
        if user_cast not in needed_casts and user_cast in known_casts:
            return explain_r(message.format(user_cast), code, tldr)
    return False


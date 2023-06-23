import ast
import dataclasses
import datetime

from pedal.core.feedback import Feedback
from pedal.sandbox.result import is_sandbox_result
from pedal.types import new_types

# acbart: Provide JSONEncoder for Skulpt compatibility
try:
    from json import JSONEncoder
except AttributeError:
    class JSONEncoder:
        pass


class PedalJSONEncoder(JSONEncoder):
    """
    Custom JSON Encoder to handle weird Pedal values nested in Feedback Functions,
    including things like SandboxResult.
    """
    def _iterencode(self, o, markers=None):
        if is_sandbox_result(o):
            return super()._iterencode(o._actual_value, markers)
        else:
            return super()._iterencode(o, markers)

    def iterencode(self, o, _one_shot=False):
        if is_sandbox_result(o):
            return super().iterencode(o._actual_value, _one_shot)
        else:
            return super().iterencode(o, _one_shot)

    def default(self, obj):
        if hasattr(obj, 'to_json'):
            return obj.to_json()
        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            return obj.isoformat()
        elif isinstance(obj, datetime.timedelta):
            return (datetime.datetime.min + obj).time().isoformat()
        elif isinstance(obj, new_types.Type):
            return str(obj)
        elif isinstance(obj, ast.AST):
            return obj.__class__.__name__
        try:
            return repr(obj)
        except:
            return '<not serializable>'


def clean_json(obj):
    if is_sandbox_result(obj):
        return clean_json(obj._actual_value)
    elif isinstance(obj, Feedback):
        return clean_json(obj.to_json())
    if isinstance(obj, dict):
        return {clean_json(key): clean_json(value) for key, value in obj.items()}
    elif isinstance(obj, (set, list, tuple)):
        return [clean_json(value) for value in obj]
    else:
        return obj

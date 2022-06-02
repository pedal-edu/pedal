"""
Standardized Report format for the result of running Pedal CLI's Stats mode.


Need to capture
    Each submission
        Errors
        Stdout?
        Feedback Functions generated
            All the usual fields
        Final Feedback chosen
    The ICS used on it
    Any metadata surrounding that
        User/Assignment/Course

I'm thinking this has a Dataframe-esque interface, where you can do things like StatReport.scripts to get all the scripts.

list of:
  script (str): The instructor code
  submission:
    user:
      email (str): User's email address
      ...
    assignment:
      name (str): The name of this assignment
    ...
    execution:
      timestamp (str)
      event_id (int)
    files (dict[str: str]): map of filenames to contents
  environment (str): what default configuration was used
  result:
    output (str): Any text piped to stdout by the instructor's code
    error (Exception): Any errors triggered by the instructor's code
    resolution:
      final:
        success (bool): Whether the final feedback was correct
        score (float): Any partial credit assigned
        category (str): The final Feedback Category chosen
        title (str): The final feedback's title
        label (str): The final feedback's label
        ...
      considered (list of): [
        correct (bool): Whether this particular feedback was correct
        active (bool): Whether this feedback was detected
        label (str): The label of this feedback
        ...
      ]
"""

def flatten_nested_json(key, data):
    result = {}
    if isinstance(data, dict):
        for subkey, value in data.items():
            flattened = flatten_nested_json(subkey, value)
            for flat_key, flat_value in flattened.items():
                result[f"{key}.{flat_key}"] = flat_value
    else:
        result[key] = data
    return result


class StatReport:
    script: str
    environment: str

    submission: dict

    result: dict

    def __init__(self, raw):
        self._raw = raw

    def __getitem__(self, item):
        if isinstance(item, int):
            return self._raw[item]
        if isinstance(item, str):
            return [r[item] for r in self._raw]

    def get_all_feedback(self, with_submissions=True):
        data = [dict(**e) if not with_submissions else
                dict(**e, **flatten_nested_json('submission', r['submission']))
                for r in self._raw
                for e in r['result']['considered']]
        return data

    def get_final_feedback(self, with_submissions=True):
        data = [dict(**r['result']['final']) if not with_submissions else
                dict(**r['result']['final'],
                     **flatten_nested_json('submission', r['submission']))
                for r in self._raw]
        return data

    def get_errors(self):
        return [r['result']['error'] for r in self._raw if r['result']['error']]

    def get_outputs(self):
        return [r['result']['output'] for r in self._raw if r['result']['output']]

    def __getattr__(self, attr):
        if attr == 'errors':
            return self.get_errors()
        elif attr == 'outputs':
            return self.get_outputs()
        raise AttributeError("%r object has no attribute %r" %
                             (self.__class__.__name__, attr))

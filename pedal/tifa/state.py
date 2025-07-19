"""
Classes and functions for managing the State of a variable.
"""
from pedal.types.new_types import is_subtype


def check_trace(state):
    """
    Create a list of all the types that this given state ever took on.

    Args:
        state (:py:class:`pedal.tifa.state.State`): The state to check the trace
            history of.

    Returns:
        list[:py:class:`pedal.types.new_types.Type`]: The list of all types
            that this State ever took on.
    """
    past_types = [state.type]
    for past_state in state.trace:
        past_types.extend(check_trace(past_state))
    return past_types


class State:
    """
    A representation of a variable at a particular point in time of the program.

    Attributes:
        name (str): The name of the variable, without its scope chain
        trace (list of State): A recursive definition of previous States for
                               this State.
        type (Type): The current type of this variable.
        method (str): One of 'store', 'read', (TODO). Indicates the change that
                      occurred to this variable at this State.
        position (dict): A Position dictionary indicating where this State
                         change occurred in the source code.
        read (str): One of 'yes', 'no', or 'maybe'. Indicates if this variable
                    has been read since it was last changed. If merged from a
                    diverging path, it is possible that it was "maybe" read.
        set (str): One of 'yes', 'no', or 'maybe'. Indicates if this variable
                    has been set since it was last read. If merged from a
                    diverging path, it is possible that it was "maybe" changed.
        over (str): One of 'yes', 'no', or 'maybe'. Indicates if this variable
                    has been overwritten since it was last set. If merged from a
                    diverging path, it is possible that it was "maybe" changed.
        over_position (dict): A Position indicating where the State was
                              previously set versus when it was overwritten.
    """

    def __init__(self, name, trace, type, method, position,
                 read='maybe', set='maybe', over='maybe', over_position=None):
        self.name = name
        self.trace = trace
        self.type = type
        self.method = method
        self.position = position
        self.over_position = over_position
        self.read = read
        self.set = set
        self.over = over

    def copy(self, method, position):
        """
        Make a copy of this State, copying this state into the new State's trace
        """
        return State(self.name, [self], self.type, method, position,
                     self.read, self.set, self.over, self.over_position)


    def perfect_copy(self):
        """
        Make a perfect copy of this State, copying this state into the new State's trace
        """
        return State(self.name, self.trace, self.type, self.method, self.position,
                     self.read, self.set, self.over, self.over_position)

    def __str__(self):
        """
        Create a string representation of this State.
        """
        return "{method}(r:{read},s:{set},o:{over},{type})".format(
            method=self.method,
            read=self.read[0],
            set=self.set[0],
            over=self.over[0],
            type=self.type.__class__.__name__
        )

    def __repr__(self):
        """
        Create a string representation of this State.
        """
        return str(self)

    def was_type(self, a_type):
        """
        Retrieve all the types that this variable took on over its entire
        trace.
        """
        from pedal.types.normalize import normalize_type
        a_type = normalize_type(a_type).as_type()
        past_types = check_trace(self)
        return any(is_subtype(past_type, a_type) for past_type in past_types)


from collections import defaultdict
import hashlib

def print_history_diagram(history):
    def state_id(path_id, name, index):
        return f"{name}_{path_id}_{index}"

    def hash_style(text):
        return hashlib.md5(text.encode()).hexdigest()[:6]

    grouped = defaultdict(list)
    for path_id, fqname, state in history:
        grouped[state.name].append((path_id, fqname, state))

    print("```mermaid")
    print("flowchart TD")

    for var_name, entries in grouped.items():
        print(f"  subgraph {var_name}")
        prev_state = None
        for idx, (path_id, fqname, state) in enumerate(entries):
            sid = state_id(path_id, state.name, idx)

            # Determine highlighted lines
            highlights = {}
            if prev_state:
                if state.read != prev_state.read:
                    highlights['read'] = True
                if state.set != prev_state.set:
                    highlights['set'] = True
                if state.over != prev_state.over:
                    highlights['over'] = True
                if state.type.__class__ != prev_state.type.__class__:
                    highlights['type'] = True

            read = f"**read: {state.read}**" if highlights.get('read') else f"read: {state.read}"
            set_ = f"**set: {state.set}**" if highlights.get('set') else f"set: {state.set}"
            over = f"**over: {state.over}**" if highlights.get('over') else f"over: {state.over}"
            type_ = f"**type: {state.type.__class__.__name__}**" if highlights.get('type') else f"type: {state.type.__class__.__name__}"

            label = f"{read}<br>{set_}<br>{over}<br>{type_}"
            print(f'    {sid}["{label}"]')

            if idx > 0:
                prev_sid = state_id(entries[idx - 1][0], entries[idx - 1][2].name, idx - 1)
                print(f'    {prev_sid} -->|{state.method}| {sid}')
            prev_state = state
        print("  end")

    print("```")
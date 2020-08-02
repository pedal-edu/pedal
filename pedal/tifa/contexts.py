"""
Context managers for dealing with paths and scopes.
"""


class NewPath:
    """
    Context manager for entering and leaving execution paths (e.g., if
    statements).)

    Args:
        tifa (Tifa): The tifa instance, so we can modify some of its
                     properties that track variables and paths.
        origin_path (int): The path ID parent to this one.
        name (str): The symbolic name of this path, typically 'i' for an IF
                    body and 'e' for ELSE body.

    Fields:
        id (int): The path ID of this path
    """

    def __init__(self, tifa, origin_path, name):
        self.tifa = tifa
        self.name = name
        self.origin_path = origin_path
        self.id = None

    def __enter__(self):
        self.tifa.path_id += 1
        self.id = self.tifa.path_id
        self.tifa.path_names.append(str(self.id) + self.name)
        self.tifa.path_chain.insert(0, self.id)
        self.tifa.name_map[self.id] = {}
        self.tifa.path_parents[self.id] = self.origin_path

    def __exit__(self, exc_type, value, traceback):
        self.tifa.path_names.pop()
        self.tifa.path_chain.pop(0)


class NewScope:
    """
    Context manager for entering and leaving scopes (e.g., inside of
    function calls).

    Args:
        tifa (Tifa): The tifa instance, so we can modify some of its
            properties that track variables and paths.
        definitions_scope_chain (list of int): The scope chain of the
            definition.
        class_type (ClassType): If this scope is a ClassType, then this
            will be available as a field.
    """

    def __init__(self, tifa, definitions_scope_chain, class_type=None):
        self.tifa = tifa
        self.definitions_scope_chain = definitions_scope_chain
        self.class_type = class_type

    def __enter__(self):
        # Manage scope
        self.old_scope = self.tifa.scope_chain[:]
        # Move to the definition's scope chain
        self.tifa.scope_chain = self.definitions_scope_chain[:]
        # And then enter its body's new scope
        self.tifa.scope_id += 1
        self.tifa.scope_chain.insert(0, self.tifa.scope_id)
        # Register as class potentially
        if self.class_type is not None:
            self.class_type.scope_id = self.tifa.scope_id
            self.tifa.class_scopes[self.tifa.scope_id] = self.class_type

    def __exit__(self, exc_type, value, traceback):
        # Finish up the scope
        self.tifa._finish_scope()
        # Leave the body
        self.tifa.scope_chain.pop(0)
        # Restore the scope
        self.tifa.scope_chain = self.old_scope

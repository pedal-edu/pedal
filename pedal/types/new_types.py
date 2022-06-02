

class Type:
    # Class static
    name: str
    singular_name: str
    plural_name: str
    # Per-Class and per-instance
    fields: dict
    immutable: bool
    parents: list

    def __init__(self, immutable, fields, parents):
        self.immutable = immutable
        self.fields = fields
        self.parents = parents

    def clone(self):
        """ Make a new instance of this Type based on the old instance """
        return self.__class__(self.immutable, self.fields.copy(), self.parents.copy())

    def __str__(self):
        return str(self.__class__.__name__)

    def precise_description(self):
        """
        Returns: A human-friendly but very precise description of this type
        """
        return self.singular_name

    def clone_mutably(self):
        """ Makes a new instance IF the type is immutable; otherwise returns this instance. """
        if self.immutable:
            return self.clone()
        else:
            return self


def is_subtype(left_type, right_type):
    pass

def is_type(a_value, a_type):
    pass

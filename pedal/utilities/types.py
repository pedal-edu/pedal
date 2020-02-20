def humanize_type(t):
    if hasattr(t, '__name__'):
        return t.__name__
    else:
        return str(t)


def humanize_types(types):
    if isinstance(types, tuple):
        return ', '.join(humanize_type(t) for t in types)
    return humanize_type(types)
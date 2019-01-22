"""
A pretty-printing dump function for the ast module.  The code was copied from
the ast.dump function and modified slightly to pretty-print.

Alex Leone (acleone ~AT~ gmail.com), 2010-01-30

From http://alexleone.blogspot.co.uk/2010/01/python-ast-pretty-printer.html
"""

from ast import AST, iter_fields, parse


def dump(node, annotate_fields=True, include_attributes=False, indent='  '):
    """
    Return a formatted dump of the tree in *node*.  This is mainly useful for
    debugging purposes.  The returned string will show the names and the values
    for fields.  This makes the code impossible to evaluate, so if evaluation is
    wanted *annotate_fields* must be set to False.  Attributes such as line
    numbers and column offsets are not dumped by default.  If this is wanted,
    *include_attributes* can be set to True.
    """

    def _format(_node, level=0):
        if isinstance(_node, AST):
            fields = [(a, _format(b, level)) for a, b in iter_fields(_node)]
            if include_attributes and _node._attributes:
                fields.extend([(a, _format(getattr(_node, a), level))
                               for a in _node._attributes])
            return ''.join([
                _node.__class__.__name__,
                '(',
                ', '.join(('%s=%s' % field for field in fields)
                          if annotate_fields else
                          (b for a, b in fields)),
                ')'])
        elif isinstance(_node, list):
            lines = ['[']
            lines.extend((indent * (level + 2) + _format(x, level + 2) + ','
                          for x in _node))
            if len(lines) > 1:
                lines.append(indent * (level + 1) + ']')
            else:
                lines[-1] += ']'
            return '\n'.join(lines)
        return repr(_node)

    if not isinstance(node, AST):
        raise TypeError('expected AST, got %r' % node.__class__.__name__)
    return _format(node)


def parseprint(code, filename="<string>", mode="exec", **kwargs):
    """Parse some code from a string and pretty-print it."""
    node = parse(code, mode=mode)  # An ode to the code
    print(dump(node, **kwargs))


# Short name: pdp = parse, dump, print
pdp = parseprint

"""
Simple data class for storing information about a location within source code.
"""

__all__ = ['Location']


class Location:
    """
    A class for storing information about a location in source code.

    Attributes:
        line (int): A line of source code.
        col (int, optional): A column within a line of source code.
            If missing, then defaults to the entire line.
        end_line (int, optional): The ending line of the source code region.
            Requires :py:attr:`line`.
        end_col (int, optional): The ending column of the source code region.
            Requires :py:attr:`col`.
        filename (str, optional): The filename that this location refers to.
            If missing, then defaults to the student's submission's main file.
    """

    def __init__(self, line, col=None, end_line=None, end_col=None,
                 filename=None):
        self.line = line
        self.col = col
        self.end_line = end_line
        self.end_col = end_col
        self.filename = filename

    @classmethod
    def from_ast(cls, node):
        """
        Creates a new Location object from the AST node. Should work
        for both built-in AST nodes and CaitNodes.

        Args:
            node (Node):

        Returns:
            Location
        """
        return Location(node.lineno, col=node.col_offset)

    def to_json(self):
        """
        Creates a JSON version of this object, with all the fields.

        Returns:
            Dict[str,Any]: The JSON version of this location information.
        """
        return {
            "line": self.line,
            "col": self.col,
            "end_line": self.end_line,
            "end_col": self.end_col,
            "filename": self.filename
        }

class Substitution:
    """

    """
    def __init__(self, code: str, filename: str):
        self.code = code
        self.filename = filename
        self.lines = code.split("\n")

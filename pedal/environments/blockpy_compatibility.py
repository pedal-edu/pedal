class GracefulExit(Exception):
    pass


class StudentData:
    def __init__(self):
        pass

    def get_names_by_type(self, type, exclude_builtins):
        pass

    def get_values_by_type(self, type, exclude_builtins):
        pass


student = StudentData()


def get_output():
    pass


def reset_output():
    pass


def queue_input(*inputs):
    pass


def get_program():
    pass


def parse_program():
    pass


def had_execution_time_error():
    pass


def limit_execution_time():
    pass


def unlimit_execution_time():
    pass


def analyze_program():
    pass


def def_use_error(AstNode):
    pass


class CorruptedAstNode:
    def __init__(self):
        pass


def find_match(instructor_code):
    pass


def find_matches(instructor_code):
    pass


class ASTMap:
    def __init__(self, JSAstMap):
        pass

    def get_std_name(self, id):
        pass

    def get_std_exp(self, id):
        pass


class AstNode:
    def __init__(self, id):
        pass

    def __eq__(self, other):
        pass

    def numeric_logic_check(self, mag, expr):
        pass

    def __str__(self):
        pass

    def __repr__(self):
        pass

    def __getattr__(self, key):
        pass

    def has(self, AstNode):
        pass

    def find_all(self, type):
        pass

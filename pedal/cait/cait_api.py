import pedal.cait.stretchy_tree_matching as tree_match


def parse_program():
    """Parses student code (attempts to retrieve from TIFA?)
    TODO: TIFA
    :return: student AST
    """
    return False


def def_use_error(node):
    """Checks if node is a name and has a def_use_error
    TODO: TIFA
    :param node: student AST name node
    :return: True if the given name has a def_use_error
    """
    return False


def find_match(ins_code, std_code=None):
    """Apply Tree Inclusion and return first match
    TODO: Implement find_match
    :param ins_code: Instructor defined pattern
    :return: First match of tree inclusion of instructor in student
    """
    if std_code is None:
        pass  # TODO: Fill in report access

    tree_matcher = tree_match.StretchyTreeMatcher(ins_code)
    matches = tree_matcher.find_matches(std_code)
    if matches:
        matches = matches[0]
    return matches


def find_matches(ins_code, std_code=None):
    """Apply Tree Inclusion and return all matches
    TODO: Implement find_matches
    :param ins_code: Instructor pattern
    :return: All matches of tree inclusion of instructor in student
    """
    if std_code is None:
        pass  # TODO: Fill in report access

    tree_matcher = tree_match.StretchyTreeMatcher(ins_code)
    return tree_matcher.find_matches(std_code)

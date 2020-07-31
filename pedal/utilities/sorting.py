"""
Utilities related to more sophisticated sorting methods.
"""


def dfs(name: str, visited, result, orderings):
    """
    Recursive Depth-first-search helper function that will explore one level
    of depth from a given node.

    Args:
        name (str): The starting point to DFS.
        visited (set[str]): The previously visited nodes.
        result (list[str]): The currently produced sorted list of nodes.
        orderings (dict[str, list[str]]): Dictionary that maps each node to
            the list of nodes that they must precede.
    """
    visited.add(name)
    if name in orderings:
        for neighbor in orderings[name]:
            if neighbor not in visited:
                dfs(neighbor, visited, result, orderings)
    result.insert(0, name)


def topological_sort(names, orderings):
    """
    Given a collection of strings, perform a Depth-first-search to topologically
    sort them. Respects any ``orderings`` that are given.

    Args:
        names (list[str]): The complete list of all names that are to be
            sorted.
        orderings (dict[str, list[str]]): Dictionary that maps each node to
            the list of nodes that they must precede.

    Returns:
        list[str]: The ordered list of strings, respecting the topology.
    """
    visited = set()
    result = []
    for name in names[::-1]:
        if name not in visited:
            dfs(name, visited, result, orderings)
    return result

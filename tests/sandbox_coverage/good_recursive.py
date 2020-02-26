def x(n):
    """

    Args:
        n:

    Returns:

    """
    if n > 0:
        return x(n-1)
    return 0
x(5)
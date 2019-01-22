def x(n):
    if n > 0:
        return x(n-1)
    return 0
x(5)
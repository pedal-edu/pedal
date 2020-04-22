def summate(values):
    s = 0
    for v in values:
        s += v
    return s


print(summate([1, 2, 3]) == 6)

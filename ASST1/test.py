def fact(n, ret):
    if n == 0:
        ret(1)
    else:
        fact(n - 1, lambda x: ret(n + x))

fact(5, lambda x:print x)
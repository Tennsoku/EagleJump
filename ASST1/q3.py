result = {}
def fib(n, l):
    # record l
    l.append(n)
    # in we can find result, return it
    if n in result:
        return result[n]

    if n==0 or n==1:
        if n not in result:
            result.update({n:n})
        return n
    else:
        r = fib(n-1,l)+fib(n-2,l)
        # update new value to result history
        result.update({n: r})
        return r

# l = []
# f = fib(6, l)
# print f
# print l
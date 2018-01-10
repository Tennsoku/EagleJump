def my_map(func, *iterable):
    argsList = zip(*iterable)
    return [func(*args) for args in argsList]

def my_filter(func, iterable):
    return [x for x in iterable if func(x)]

def my_reduce(function, iterable, initializer=None):
    it = iter(iterable)
    if initializer is None:
        try:
            initializer = next(it)
        except StopIteration:
            raise TypeError('reduce() of empty sequence with no initial value')
    accum_value = initializer
    for x in it:
        accum_value = function(accum_value, x)
    return accum_value

# a = [1,2,3,4]
# b = [17,12,11,10]
# c = [-1,-4,5,9]
# print map(lambda x,y:x*y, a, b)
# print my_map(lambda x,y:x*y, a, b)
#
# fib = [0,1,1,2,3,5,8,13,21,34,55]
# print filter(lambda x: x % 2, fib)
# print my_filter(lambda x: x % 2, fib)
#
# print reduce(lambda x,y: x+y, [47,11,42,13])
# print my_reduce(lambda x,y: x+y, [47,11,42,13])
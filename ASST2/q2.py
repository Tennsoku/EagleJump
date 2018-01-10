def find_product(l):
    limit = len(l) - 4
    set = map(lambda x: (x,x+5), range(limit))
    sublist = map(lambda x: list(l[x[0]:x[1]]), set)
    productList = map(lambda x: reduce(lambda y,z: y*z, x), sublist)
    resultList = list(enumerate(productList))
    resultList.sort(key = lambda t: t[1], reverse=False)
    return resultList[-1]

# print find_product([1,2,3,4,5,6,4,2,1,3])
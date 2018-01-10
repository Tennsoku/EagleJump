def rotate(a, b):
    # result = [rotated letters] + [unrotated letters]
    return  a[b%len(a):]+a[:b%len(a)]

# print rotate('abc',2)
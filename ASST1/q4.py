import doctest

def factorize(N):
# doctest cases
    """
    >>> factorize(6)
    [1, 2, 3]
    >>> factorize(21)
    [1, 3, 7]
    >>> factorize(45)
    [1, 3, 3, 5]
    >>> factorize(81)
    [1, 3, 3, 3, 3]
    """
    # 1 is in every output no matter what is input
    # Hey, 1 is not prime!
    result = [1]
    prime = 2
    # the largest prime should smaller than its sqrt
    while prime*prime <= N:
        # if > 0, N now contains no more current prime as factor
        while (N % prime)==0:
            result.append(prime)
            N //= prime
        prime += 1
    if N > 1:
        result.append(N)
    return result

if __name__=="__main__":
    doctest.testmod()
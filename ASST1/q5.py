import math

def Q(D):
    C = 50
    H = 30
    # find nearest int (not rounded. floor here.)
    return [int(math.sqrt((2*C*i)/H)) for i in D]

# print Q([100,150,180])
from time import clock

PROFILE_RUSULTS = {}
PROFILE_FUNCTIONS = True

def profile(func):
    global PROFILE_FUNCTIONS,PROFILE_RUSULTS
    def wrapper(*args,**kwargs):
        if PROFILE_FUNCTIONS:
            start = clock()
            retVal = func(*args,**kwargs)
            duration = clock() - start
            if func in PROFILE_RUSULTS:
                avg = PROFILE_RUSULTS[func.__name__][0]
                times = PROFILE_RUSULTS[func.__name__][1]
                newAvg = (avg * times + duration)/(times + 1)
                PROFILE_RUSULTS[func.__name__] = (newAvg, times + 1)
            else:
                PROFILE_RUSULTS[func.__name__]=(duration,1)
            return retVal
        else:
            retVal = func(*args, **kwargs)
            return retVal
    return wrapper


@profile
def test():
    print("test")
    return

# test()
# print PROFILE_RUSULTS




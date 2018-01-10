import collections, itertools

class readFile(object):
    f = None
    def __init__(self, filename):
        global f
        f = open(filename, 'r')
        self.line = f.readline()
        self.words = self.line.split()
        self.index = 0
    def __iter__(self):
        return self
    def next(self):
        if not self.line:
            raise StopIteration
        result = self.words[self.index]
        self.index += 1
        if self.index > len(self.words)-1:
            self.line = f.readline()
            self.words = self.line.split()
            self.index = 0
        return result
    def __del__(self):
        f.close()


def find_popular(filename):
    dict = {}
    words = readFile(filename)
    if not words:
        print "Read Failed!"
        return []

    for i in words:
        if i in dict:
            dict[i] += 1
        else:
            dict[i] = 1
    ordered = collections.OrderedDict(sorted(dict.items(), key=lambda t: t[1], reverse=True))
    topWords = list(itertools.islice(ordered.iteritems(), 10))
    return [x[0] for x in topWords]


# print find_popular("q4test.txt")
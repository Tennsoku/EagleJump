class Count:
    def __init__(self, n):
        self.max = n

    def __iter__(self):
        self.count = 0
        return self

    def __next__(self):
        if self.count == self.max:
            raise StopIteration
        self.count += 1
        return self.count - 1

if __name__ == '__main__':
    c = Count(4)
    for i in c:
        print(i)
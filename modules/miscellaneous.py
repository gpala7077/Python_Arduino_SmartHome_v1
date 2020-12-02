
class Queue:
    def __init__(self, style):
        self.queue = []
        self.style = style

    def add(self, element):

        if self.style == 'FIFO':
            self.queue.append(element)

        elif self.style == 'LIFO':
            self.queue.insert(0, element)

    def get(self):
        return self.queue.pop(0)

    def __bool__(self):
        return len(self.queue) > 0

    def __repr__(self):
        return ', '.join(self.queue)

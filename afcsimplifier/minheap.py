import heapq
# source: http://joernhees.de/blog/2010/07/19/min-heap-in-python/

class Heap(object):
    """ A neat min-heap wrapper which allows storing items by priority
        and get the lowest item out first (pop()).
        Also implements the iterator-methods, so can be used in a for
        loop, which will loop through all items in increasing priority order.
        Remember that accessing the items like this will iteratively call
        pop(), and hence empties the heap! """
   
    def __init__(self):
        """ create a new min-heap. """
        self._heap = []

    def head(self):
        return self._heap[0][1]

    def push(self, priority, item):
        """ Push an item with priority into the heap.
            Priority 0 is the highest, which means that such an item will
            be popped first."""
        assert priority >= 0
        heapq.heappush(self._heap, (priority, item))
    def set_priority(self, priority, item, new_priority):
        i = self._heap.index((priority, item))
        self._heap[i] = self._heap[-1]
        self._heap.pop()

        if i < len(self._heap):
            heapq._siftup(self._heap, i)
        self.push(new_priority, item)

    def pop(self):
        """ Returns the item with lowest priority. """
        return heapq.heappop(self._heap)[1] # (prio, item)
   
    def __len__(self):
        return len(self._heap)
   
    def __iter__(self):
        """ Get all elements ordered by asc. priority. """
        return self
   
    def next(self):
        """ Get all elements ordered by their priority (lowest first). """
        try:
            return self.pop()
        except IndexError:
            raise StopIteration


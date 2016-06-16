'''
Created on Sep 6, 2013

@author: albert
'''
import simplipy.geotool as geotool
from simplipy.util import P_REMOVED, P_COORD, to_points_data, DIRECTION_NORMAL, DIRECTION_REVERSE

class minHeap(object):
    def __init__(self):
        self.heap = {}
        self.q = []

    def __len__(self):
        return len(self.q)

    def head(self):
        return self.q[0]

    def push(self, value):
        self.q.append(value)
        i = len(self.q)-1
        value.__heap_index = i
        self.up(i)

    def pop(self):
        # replace first element by last element in the heap
        first = self.q[0]
        last = self.q.pop()
        if len(self.q) > 0:
            last.__heap_index = 0
            self.q[0] = last
            self.down(0)
        return first

    def update_key(self, obj, old_area):
        i = obj.__heap_index
        if old_area <= obj.area:
            self.down(i)
        else:
            self.up(i)

    def remove(self, removed):
        i = removed.__heap_index
        last = self.q.pop()
        if (i != len(self.q)):
            last.__heap_index = i
            self.q[i] = last
            if (last.area < removed.area):
                self.up(i)
            else:
                self.down(i)
        return i

    def up(self, i):
        obj = self.q[i]
        while i > 0:
            iup = ((i+1)>>1) - 1
            parent = self.q[iup]
            if (obj.area >= parent.area):
                break
            parent.__heap_index = i
            self.q[i] = parent

            i = iup
            obj.__heap_index = i
            self.q[i] = obj

    def down(self, i):
        obj = self.q[i]
        n = len(self.q)
        down = i
        while True:
            right = (i+1) << 1
            left = right-1
            child = obj
            if (left < n and self.q[left].area < child.area):
                down = left
                child = self.q[down]
            if (right < n and self.q[right].area < child.area):
                down = right
                child = self.q[down]
            if (down == i):
                return
            child.__heap_index = i
            self.q[i] = child

            i = down
            obj.__heap_index = i
            self.q[i] = obj

class Point(object):
    def __init__(self, p):
        self.p = p
        self.area = None
        self.prev = None
        self.next = None

    def calc_area(self):
        self.area = geotool.area(self.p[P_COORD], self.prev.p[P_COORD], self.next.p[P_COORD])
        return self.area


def visvalingam(chain, minArea=0.01, ring_min_points=3):
    if chain[0] == chain[-1]:
        is_ring = True
        chain = chain[:-1]
    else:
        is_ring = False
    # Ported to python from javascript: http://bost.ocks.org/mike/simplify/
    n = len(chain)

    # Prepare data structures
    effective_area = minHeap()
    points = map(Point, chain)

    # Create linked list
    i = 0
    while i < n-1:
        points[i].next = points[i+1]
        points[i+1].prev = points[i]
        i += 1
    points[-1].next = points[0]
    points[0].prev = points[-1]

    # Compute efficient area
    maxArea = 0
    for p in points:
        area = p.calc_area()
        if area > maxArea:
            maxArea = area
        effective_area.push(p)

    def update(p):
        old_area = p.area
        p.calc_area()
        effective_area.update_key(p, old_area)

    min_points = ring_min_points if is_ring else 2
    while len(effective_area) > min_points and effective_area.head().area < minArea:
        p = effective_area.pop() # Point with the lowest effective area
        p.p[P_REMOVED] = True
        # If the area of the current point is less than that of the previous point
        # to be eliminated, use the latter's area instead. This ensures that
        # the current point cannot be eliminated without eliminating previously-
        # eliminated points.
        p.area = maxArea = max(p.area, maxArea) # TODO: check this, may affect minheap update_key!

        p.prev.next = p.next
        p.next.prev = p.prev
        update(p.prev)
        update(p.next)

    if not is_ring:
        chain[0][P_REMOVED] = False
        chain[-1][P_REMOVED] = False

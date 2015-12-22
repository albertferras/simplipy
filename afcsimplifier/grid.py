'''
Created on Sep 6, 2013

@author: albert
'''
import math


def boxid_raytrace(pab, k):
    """ "Raytrace" a line pab into a bitmap grid of size k. Returns all bitmap (x, y) positions where the line pass.
    
    Actually, it's the Supercover DDA Algorithm

     Ported from http://stackoverflow.com/questions/18881456/supercover-dda-algorithm
     which is based on http://lodev.org/cgtutor/raycasting.html
    """
    if pab[0] < pab[1]:
        (x0, y0), (x1, y1) = pab
    else:
        (x1, y1), (x0, y0) = pab
    x0 /= k
    y0 /= k
    x1 /= k
    y1 /= k

    vx = x1 - x0
    vy = y1 - y0
    ix = int(x0)
    iy = int(y0)

    if vx == 0:  # vertical line
        inc = 1 if vy > 0 else -1
        iy2 = int(y1)
        while iy != iy2:
            yield ix, iy
            iy += inc
        yield ix, iy
        return
    elif vy == 0:  # horizontal line
        inc = 1 if vx > 0 else -1
        ix2 = int(x1)
        while ix != ix2:
            yield ix, iy
            ix += inc
        yield ix, iy
        return

    dx = math.sqrt(1 + (vy/vx)**2)
    dy = math.sqrt(1 + (vx/vy)**2)

    if vx < 0:
        sx = -1
        ex = (x0 - ix) * dx
    else:
        sx = 1
        ex = (ix + 1 - x0) * dx

    if vy < 0:
        sy = -1
        ey = (y0 - iy) * dy
    else:
        sy = 1
        ey = (iy + 1 - y0) * dy

    n = math.sqrt(vx**2 + vy**2)
    while min(ex, ey) <= n:
        yield ix, iy
        if ex < ey:
            ex += dx
            ix += sx
        else:
            ey += dy
            iy += sy
    yield ix, iy


class Grid(object):
    def __init__(self, width=0.05):
        self.boxes = {}
        self.K = width

    def _box_ids(self, pab):
        return boxid_raytrace(pab, self.K)

    def add(self, key, pab):
        for box_id in self._box_ids(pab):
            box = self.boxes.get(box_id)
            if box is None:
                box = []
                self.boxes[box_id] = box
            box.append(key)

    def hit(self, pab):
        hits = set()
        for box_id in self._box_ids(pab):
            keys = self.boxes.get(box_id)
            if keys is not None:
                for key in keys:
                    hits.add(key)
        return hits

    def get_pairs(self):
        for keys in self.boxes.itervalues():
            # todo: optimize
            n = len(keys)
            if n > 1:
                for i in range(n):
                    key1 = keys[i]
                    for j in range(i+1, n):
                        yield (key1, keys[j])

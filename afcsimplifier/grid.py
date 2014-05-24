'''
Created on Sep 6, 2013

@author: albert
'''
import operator


def raytrace(x0, y0, x1, y1):
    dx = abs(x1 - x0);
    dy = abs(y1 - y0);
    x = x0;
    y = y0;
    n = 1 + dx + dy;
    x_inc = 1 if (x1 > x0) else -1;
    y_inc = 1 if (y1 > y0) else -1;
    error = dx - dy;
    dx *= 2;
    dy *= 2;
    while n > 0:
        yield (x,y)
        n -= 1
        if error > 0:
            x += x_inc
            error -= dy
        else:
            y += y_inc
            error += dx

class Grid(object):
    def __init__(self, width=0.05):
        self.boxes = {}
        self.K = width

    def _box_ids(self, pab):
        ax = int(pab[0][0]/self.K)
        ay = int(pab[0][1]/self.K)
        bx = int(pab[1][0]/self.K)
        by = int(pab[1][1]/self.K)
        return raytrace(ax, ay, bx, by)


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



if __name__ == '__main__':
    segments = [
        ((120, 230), (270, 330)),
        ((180, 180), (340, 300)),
        ((240, 150), (220, 350)),
        ((320, 310), (430, 150)),
        ((740, 450), (660, 100)),
        ((160, 440), (510, 350)),
        ((550, 550), (510, 350)),
        ((-1.595, 43.718), (0.261, 43.534)),
        ((-1.442, 43.638), (-1.302, 44.148)),
    ]
    G = Grid(100)
    for (key, pab) in enumerate(segments):
        G.add(key, pab)
    print G.boxes
    #
    # import geotool
    # qt = QuadTree(segs)
    # for s1 in segs:
    #     hits = qt.hit(s1)
    #     for key in hits:
    #         if s1[0] >= key:
    #             continue
    #         s2 = segs[key]
    #
    #
    #         l1 = segments[s1[0]]
    #         l2 = segments[s2[0]]
    #         print "%s x %s = %s" % (s1[0], s2[0], geotool.crosses(l1, l2))
    #
    #

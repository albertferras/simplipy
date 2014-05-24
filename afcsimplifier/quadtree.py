'''
Created on Sep 6, 2013

@author: albert
'''
import operator
import copy
_get_point_x = operator.itemgetter(0)
_get_point_y = operator.itemgetter(1)


LEFT = 0
RIGHT = 1
BOTTOM = 2
TOP = 3
def segment(key, pa, pb):
    bbox = (min(pa[0], pb[0]), # left
            max(pa[0], pb[0]), # right
            min(pa[1], pb[1]), # bottom
            max(pa[1], pb[1]), # top
            )
    return (key, bbox)

class QuadTree(object):
    QT_MAX_NODE_SIZE = 200
    QT_MAX_DEPTH = 128
    def __init__(self, items, bounding_rect=None, level=0):
        # items is a list of tuples (id, bbox)
        self.q1 = self.q2 = self.q3 = self.q4 = None
        # q1 = Upper-left
        # q2 = Upper-right
        # q3 = Bottom-left
        # q4 = Bottom-right
        self.level = level

        if bounding_rect is None:
            l = min(item[1][LEFT] for item in items)
            r = max(item[1][RIGHT] for item in items)
            b = min(item[1][BOTTOM] for item in items)
            t = max(item[1][TOP] for item in items)
            self.bbox = (l,t,r,b)
        else:
            self.bbox = bounding_rect



        self.cx = (self.bbox[LEFT]+self.bbox[RIGHT])/2.0
        self.cy = (self.bbox[BOTTOM]+self.bbox[TOP])/2.0

        self.haschildren = False
        self.items = []
        self.add_items(items)


    def _items_to_quadrants(self, items):
        q1_items = []
        q2_items = []
        q3_items = []
        q4_items = []
        for item in self.items:
            # in which quadrant is our geometry contained?
            bbox = item[1]

            in_left = bbox[LEFT] < self.cx
            in_right = bbox[RIGHT] >= self.cx
            in_bot = bbox[BOTTOM] < self.cy
            in_top = bbox[TOP] >= self.cy

            if in_left and in_top: q1_items.append(item)
            if in_right and in_top: q2_items.append(item)
            if in_left and in_bot: q3_items.append(item)
            if in_right and in_bot: q4_items.append(item)
        return (q1_items, q2_items, q3_items, q4_items)

    def _move_to_quadrants(self, items):
        (q1_items, q2_items, q3_items, q4_items) = self._items_to_quadrants(items)
        if not self.haschildren:
            nq = bool(q1_items) + bool(q2_items) + bool(q3_items) + bool(q4_items)
            if nq == 1:
                return
        if q1_items:
            if self.q1 is None:
                self.q1 = QuadTree(q1_items, (self.bbox[LEFT], self.cx, self.cy, self.bbox[TOP]),self.level+1)
            else:
                self.q1.add_items(q1_items)
        if q2_items:
            if self.q2 is None:
                self.q2 = QuadTree(q2_items, (self.cx, self.bbox[RIGHT], self.cy, self.bbox[TOP]),self.level+1)
            else:
                self.q2.add_items(q2_items)
        if q3_items:
            if self.q3 is None:
                self.q3 = QuadTree(q3_items, (self.bbox[LEFT], self.cx, self.bbox[BOTTOM], self.cy),self.level+1)
            else:
                self.q3.add_items(q3_items)
        if q4_items:
            if self.q4 is None:
                self.q4 = QuadTree(q4_items, (self.cx, self.bbox[RIGHT], self.bbox[BOTTOM], self.cy),self.level+1)
            else:
                self.q4.add_items(q4_items)
        self.haschildren = True
        self.items = []

    def add_items(self, items):
        if self.haschildren:
            self._move_to_quadrants(items)
        else:
            self.items.extend(items)
            if len(self.items) > self.QT_MAX_NODE_SIZE and self.level >= self.QT_MAX_DEPTH:
                #print "max depth reached: %s items" % len(self.items)
                pass
            if len(self.items) > self.QT_MAX_NODE_SIZE and self.level <= self.QT_MAX_DEPTH:
                self._move_to_quadrants(self.items)

    def _hit(self, bboxB, overlaps_func):
        # tab = " "*self.level
        # print "%sHIT (%s)" % (tab, self.bbox,)
        # if len(self.items)>0:
        #     print "%sITEMS=%s" % (tab, len(self.items))
        results = filter(overlaps_func, self.items)
        #results = copy.copy(self.items)
        if len(results) > 0:
            results = map(operator.itemgetter(0), results)
        if self.haschildren:
            in_left = bboxB[LEFT] < self.cx
            in_right = bboxB[RIGHT] >= self.cx
            in_bot = bboxB[BOTTOM] < self.cy
            in_top = bboxB[TOP] >= self.cy
            if self.q1 and in_left and in_top:
                results.extend(self.q1._hit(bboxB, overlaps_func))
            if self.q2 and in_right and in_top:
                results.extend(self.q2._hit(bboxB, overlaps_func))
            if self.q3 and in_left and in_bot:
                results.extend(self.q3._hit(bboxB, overlaps_func))
            if self.q4 and in_right and in_bot:
                results.extend(self.q4._hit(bboxB, overlaps_func))
        return results


    def hit(self, item):
        # returns the id of items that overlap the bounding of a item
        bboxB = item[1]
        # print "INPUT (%s)" % (bboxB,)
        def overlaps_func(item2):
            bboxA = item2[1]
            return bboxA[RIGHT] >= bboxB[LEFT] and bboxA[LEFT] <= bboxB[RIGHT] and \
                   bboxA[BOTTOM] <= bboxB[TOP] and bboxA[TOP] >= bboxB[BOTTOM]
        return set(self._hit(bboxB, overlaps_func))


if __name__ == '__main__':
    segments = [
        # ((120, 230), (270, 330)),
        # ((180, 180), (340, 300)),
        # ((240, 150), (220, 350)),
        # ((320, 310), (430, 150)),
        # ((740, 450), (660, 100)),
        # ((160, 440), (510, 350)),
        # ((550, 550), (510, 350)),
        ((-1.595, 43.718), (0.261, 43.534)),
        ((-1.442, 43.638), (-1.302, 44.148)),
    ]
    segs = map(lambda (i,s): segment(i,s[0], s[1]), enumerate(segments))

    import geotool
    qt = QuadTree(segs)
    for s1 in segs:
        hits = qt.hit(s1)
        for key in hits:
            if s1[0] >= key:
                continue
            s2 = segs[key]


            l1 = segments[s1[0]]
            l2 = segments[s2[0]]
            print "%s x %s = %s" % (s1[0], s2[0], geotool.crosses(l1, l2))



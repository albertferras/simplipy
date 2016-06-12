#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import unittest
import random
from afcsimplifier.geotool import distance, qdistance
from afcsimplifier.geotool_py import crosses as crosses_py
from afcsimplifier.geotool_c import crosses as crosses_c


def rand_point():
    return (random.random(), random.random())

class TestGeoTool(unittest.TestCase):
    def test_distance(self):
        cases = [((-3.945, 0.718), (-11.091, -11.741), 14.362868689784781),
                 ((-13.213, 2.417), (-3.39, 14.324), 15.435931393991098),
                 ((-4.671, 6.834), (3.676, 2.781), 9.278966429511426),
                 ((-1.98, 9.318), (-5.526, -9.722), 19.36738794985013),
                 ((4.334, 5.911), (-3.203, -2.28), 11.130986029997521),
                 ((-0.9, -9.9), (0.163, 6.85), 16.783696523710145),
                 ((4.355, 12.574), (1.742, 7.319), 5.868798343783845),
                 ((0, 0), (0, 0), 0)]
        for p1, p2, expected_distance in cases:
            dist = distance(p1, p2)
            qdist = qdistance(p1, p2)
            self.assertAlmostEqual(dist, expected_distance)
            self.assertAlmostEqual(dist ** 2, qdist)

    def _test_crosses(self, x1, y1, x2, y2, u1, v1, u2, v2, endpoint_intersects):
        c = crosses_c(x1, y1, x2, y2, u1, v1, u2, v2, endpoint_intersects=endpoint_intersects)
        py = crosses_py(x1, y1, x2, y2, u1, v1, u2, v2, endpoint_intersects=endpoint_intersects)
        if c != py:
            print "Fail for parameters:"
            print x1, y1, x2, y2, u1, v1, u2, v2
            self.fail("C and PY implementation return distinct results (C=%s, PY=%s)" % (c, py))

    def test_crosses(self):
        random.seed(0)
        for endpoint_intersects in (True, False):
            for case in xrange(50000):
                # print "------------"
                x1, y1 = rand_point()
                x2, y2 = rand_point()
                u1, v1 = rand_point()
                u2, v2 = rand_point()
                self._test_crosses(x1, y1, x2, y2, u1, v1, u2, v2, endpoint_intersects)

                self._test_crosses(x1, y1, x2, y2, x1, y1+1e-8, u2, v2, endpoint_intersects)




if __name__ == "__main__":
    unittest.main()

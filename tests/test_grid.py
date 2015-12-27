#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import math
import unittest
import random
from afcsimplifier.grid import Grid, boxid_raytrace

# Pairs of segment that intersect
PAIR_SEGMENT_INT = [[((-74.394520637, -51.122247003), (-74.495432095, -51.049248956)),
                     ((-74.473459439, -51.069105727), (-74.460275845, -51.062107029))],
                    [((107.0098, 10.5390), (106.9978, 10.5491)),
                     ((106.9978, 10.6249), (107.0114, 10.5219))],
                    ]


class TestGrid(unittest.TestCase):
    def _gen_grid_combinations(self, line1, line2):
        for s1 in (line1, reversed(line1)):
            s1 = tuple(s1)
            for s2 in (line2, reversed(line2)):
                s2 = tuple(s2)
                grid = Grid(width=0.015)
                grid.add(1, s1)
                grid.add(2, s2)
                yield grid

    def _print_grid(self, grid, box_ascii=False):
        print "Grid width=", grid.K
        all_keys = set()
        for boxid, keys in sorted(grid.boxes.iteritems()):
            # print boxid, "==", keys
            all_keys.update(keys)

        if box_ascii:
            min_x = min(grid.boxes.iterkeys(), key=lambda b: b[0])[0]
            max_x = max(grid.boxes.iterkeys(), key=lambda b: b[0])[0]
            min_y = min(grid.boxes.iterkeys(), key=lambda b: b[1])[1]
            max_y = max(grid.boxes.iterkeys(), key=lambda b: b[1])[1]
            w = (max_x - min_x) + 1
            h = (max_y - min_y) + 1
            for key in all_keys:
                print "Key = ", key
                matrix = [['.'] * w for _ in range(h)]
                for boxid, keys in grid.boxes.iteritems():
                    if key in keys:
                        x, y = boxid
                        x -= min_x
                        y -= min_y
                        matrix[y][x] = 'X'
                for line in reversed(matrix):
                    print ''.join(line)

    def test_raytrace(self):
        for grid_size in [0.015, 0.02, 0.1]:
            cases = [((106.9978, 10.6249), (107.0114, 10.5219)),
                     ((107.0098, 10.5390), (106.9978, 10.5491))]
            for k in [grid_size, grid_size * 2, grid_size / 2]:
                cases.extend([((0, 0), (-k, 0)),
                              ((0, 0), (-k, -k)),
                              ((0, 0), (-k, k)),
                              ((0, 0), (k, 0)),
                              ((0, 0), (k, -k)),
                              ((0, 0), (k, k)),
                              ((0, 0), (0, 0)),
                              ((0, 0), (0, -k)),
                              ((0, 0), (0, k))])

            random.seed(0)
            num_random_cases = 0
            for i in xrange(num_random_cases):
                x0 = random.random() * 50
                y0 = random.random() * 50
                x1 = random.random() * 50
                y1 = random.random() * 50
                if (x0, y0) == (x1, y1):
                    # Invalid line
                    continue
                line = ((x0, y0), (x1, y1))
                cases.append(line)

            for line in cases:
                boxids1 = list(boxid_raytrace(line, grid_size))
                boxids2 = list(boxid_raytrace(line[::-1], grid_size))
                if sorted(boxids1) != sorted(boxids2):
                    raise self.failureException("Distinct boxids!")

            # same box line
            line = ((0, 0), (0, 0))
            boxids = list(boxid_raytrace(line, grid_size))
            self.assertTrue(len(boxids) == 1)

            for n in xrange(1, 5):
                d = grid_size / 2
                # horizontal
                line = ((0, d), (0, grid_size * n - d))
                boxids = list(boxid_raytrace(line, grid_size))
                self.assertTrue(len(boxids) == n)
                # vertical
                line = ((d, 0), (grid_size * n - d, 0))
                boxids = list(boxid_raytrace(line, grid_size))
                self.assertTrue(len(boxids) == n)
                # diagonal
                line = ((d, d), (grid_size * n - d, grid_size * n - d))
                boxids = list(boxid_raytrace(line, grid_size))
                # note: expect raytrace to do something like this:
                #   THIS          not this:
                #   ---X          ---X
                #   --XX          --X-
                #   -XX-          -X--
                #   XX--          X---
                self.assertTrue(len(boxids) == (n * 2 - 1))

    def test_hit(self):
        for line1, line2 in PAIR_SEGMENT_INT:
            for grid in self._gen_grid_combinations(line1, line2):
                try:
                    self.assertIn(2, grid.hit(line1))
                    self.assertIn(1, grid.hit(line2))
                except AssertionError:
                    print "Failed on grid. Expected intersection between"
                    print "segment 1:", line1
                    print "segment 2:", line2
                    self._print_grid(grid, box_ascii=True)
                    print 1, list(grid._box_ids(line1))
                    print 2, list(grid._box_ids(line2))
                    raise


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import itertools
import unittest
import shapely.geometry
import shapely.wkb
from simplipy.simplifier import ChainDB
from simplipy.topology import snap_coordinates


class TestSnap(unittest.TestCase):
    def setUp(self):
        print "-------------------------"

    def _snap_points(self, geometries, snap_distance):
        chaindb = ChainDB()
        for key, geom in geometries.iteritems():
            chaindb.add_geometry(key, geom.wkb)
        snap_coordinates(chaindb, snap_distance)
        snapped_geoms = {}
        for key in geometries.iterkeys():
            snapped_geoms[key] = shapely.wkb.loads(chaindb.to_wkb(key))
        return snapped_geoms

    def test_snap(self):
        coords = [(0.0, 0.0), (-1.0, 1.0), (1.0, -0.5), (0.0, 0.0)]
        geometries = {'A': shapely.geometry.Polygon(coords)}

        # Big snap should snap all points into one
        for snap_distance, expected_num_points in ((2, 1),
                                                   (1.414213562373095, 2),
                                                   (1.414213562373096, 1)):
            snapped_geoms = self._snap_points(geometries, snap_distance=snap_distance)
            num_points = len(set(snapped_geoms['A'].exterior.coords))
            self.assertEquals(num_points, expected_num_points)

        coords = [(0.0, 0.0), (43.1234567, 12.456789876), (43.1234566, 12.456789876), (0.0, 0.0)]
        geometries = {'A': shapely.geometry.Polygon(coords)}
        snapped_geoms = self._snap_points(geometries, snap_distance=0.00000011)
        num_points = len(set(snapped_geoms['A'].exterior.coords))
        self.assertEquals(num_points, 2)

        snapped_geoms = self._snap_points(geometries, snap_distance=0.00000001)
        num_points = len(set(snapped_geoms['A'].exterior.coords))
        self.assertEquals(num_points, 3)

if __name__ == "__main__":
    unittest.main()

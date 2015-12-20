#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import unittest
import os
from afcsimplifier.geotool import distance, qdistance
from afcsimplifier.douglaspeucker import douglaspeucker
from utils import TestCaseGeometry, load_wkt, load_shapefile

data_dir = os.path.join(os.path.dirname(__file__), 'data')


def data_path(name):
    return os.path.join(data_dir, name)


class TestRepairIntersections(TestCaseGeometry):
    def setUp(self):
        print "-------------------------"

    def test_nations(self):
        geometries = load_shapefile(data_path('naturalearth_nations/ne_10m_admin_0_countries.shp'),
                                    geom_key='ISO_A2')
        # geometries = {k: v for k, v in geometries.iteritems() if k.endswith('FI')}
        constraints = dict(repair_intersections=True,
                           repair_intersections_precision=0.001)
        simplifier = douglaspeucker
        simplifier_params = dict(epsilon=0.01)
        geometries_removed = 0  # Number of geometries that disappeared (too much simplification)
        for gid, simp_wkb in self.simplify_geometries(geometries, simplifier, simplifier_params, constraints):
            if simp_wkb is None:
                geometries_removed += 1
                continue
            try:
                self.assertValidGeometry(simp_wkb)
                self.assertSimpleGeometry(simp_wkb)
            except AssertionError:
                print "Failed on geometry id={}".format(gid)
                raise
        print "Geometries removed = ", geometries_removed

    def test_line_first_and_last_segment_intersects_after_simplify(self):
        constraints = dict(repair_intersections=True,
                           repair_intersections_precision=0.001)
        simplifier = douglaspeucker
        simplifier_params = dict(epsilon=150)
        line_geom = load_wkt(data_path('line1.wkt'))
        simp_wkb = self.simplify_geometry(line_geom.wkb, simplifier, simplifier_params, constraints)
        self.assertValidGeometry(simp_wkb)
        self.assertSimpleGeometry(simp_wkb)


if __name__ == "__main__":
    unittest.main()

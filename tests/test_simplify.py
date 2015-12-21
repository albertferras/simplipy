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


# constraints:
# expandcontract=None,
# repair_intersections=False,
# repair_intersections_precision=0.01,
# prevent_shape_removal=None,
# prevent_shape_removal_min_points=3,
# use_topology=False,
# use_topology_snap_precision=0.0001,
# simplify_shared_edges=False,
# simplify_non_shared_edges=False,


class TestSimplifier(TestCaseGeometry):
    def setUp(self):
        print "-------------------------"

    def _test_geometry_simplification(self, geometries, simplifier, simplifier_params, constraints,
                                      check_valid=True, check_simple=True):
        if not isinstance(geometries, dict):
            geometries = {'A': geometries}
        geometries_removed = 0
        for gid, simp_wkb in self.simplify_geometries(geometries, simplifier, simplifier_params, constraints):
            if simp_wkb is None:
                geometries_removed += 1
                continue
            try:
                if check_valid:
                    self.assertValidGeometry(simp_wkb)
                if check_simple:
                    self.assertSimpleGeometry(simp_wkb)
            except AssertionError:
                print "Failed on geometry id={}".format(gid)
                raise
        print "Geometries removed = ", geometries_removed

    def test_preserve_topology(self):
        geometries = load_shapefile(data_path('naturalearth_nations/ne_10m_admin_0_countries.shp'),
                                    geom_key='ISO_A2')
        simplifier = douglaspeucker
        simplifier_params = dict(epsilon=0.01)
        constraints = dict(use_topology=True,
                           use_topology_snap_precision=0.0001,
                           simplify_shared_edges=True,
                           simplify_non_shared_edges=True)
        self._test_geometry_simplification(geometries, simplifier, simplifier_params, constraints,
                                           check_valid=False, check_simple=True)

    def test_repair_intersections(self):
        geometries = load_shapefile(data_path('naturalearth_nations/ne_10m_admin_0_countries.shp'),
                                    geom_key='ISO_A2')
        simplifier = douglaspeucker
        simplifier_params = dict(epsilon=0.01)
        constraints = dict(repair_intersections=True,
                           repair_intersections_precision=0.001)
        self._test_geometry_simplification(geometries, simplifier, simplifier_params, constraints,
                                           check_valid=True, check_simple=True)

    def test_line_first_and_last_segment_intersects_after_simplify(self):
        line_geom = load_wkt(data_path('line1.wkt'))
        simplifier = douglaspeucker
        simplifier_params = dict(epsilon=150)
        constraints = dict(repair_intersections=True,
                           repair_intersections_precision=0.001)
        self._test_geometry_simplification(line_geom.wkb, simplifier, simplifier_params, constraints,
                                           check_valid=True, check_simple=True)


if __name__ == "__main__":
    unittest.main()

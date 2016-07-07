#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import unittest
import os
import ogr
import shapely.wkb
from simplipy.simplifier import ChainDB
from simplipy.douglaspeucker import douglaspeucker
from utils import TestCaseGeometry, load_wkt, load_wkb, load_shapefile

data_dir = os.path.join(os.path.dirname(__file__), 'data')


def data_path(name):
    return os.path.join(data_dir, name)


# constraints:
# expandcontract=None,
# repair_intersections=False,
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
        geometries_removed = set()
        simp_geometries = {}
        for gid, simp_wkb in self.simplify_geometries(geometries, simplifier, simplifier_params, constraints):
            if simp_wkb is None:
                geometries_removed.add(gid)
                continue
            try:
                simp_geometries[gid] = simp_wkb
                if check_valid:
                    self.assertValidGeometry(simp_wkb)
                if check_simple:
                    self.assertSimpleGeometry(simp_wkb)
            except AssertionError:
                print "Failed on geometry id={}".format(gid)
                raise
        # self.save_shapefile(data_path('test'), 'simp', simp_geometries)
        if constraints.get('prevent_shape_removal') is True:
            self.assertEquals(len(geometries_removed), 0,
                              msg="Expected 0 geometries removed, but disapparead: {}"
                              .format(list(geometries_removed)))
        return simp_geometries

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

    def test_expandcontract(self):
        geometries = load_shapefile(data_path('naturalearth_nations/ne_10m_admin_0_countries.shp'), geom_key='ISO_A2')
        # geometries = load_shapefile(data_path('hrp00b11m/canada.shp'), geom_key='HR_UID')  # A LOT OF MEMORY REQUIRED
        # geometries = {k: v for k, v in geometries.iteritems() if k.split(":")[1] == 'AQ'}
        # geometries = {fname: load_wkt(data_path(fname)).wkb for fname in ['poly1.wkt', 'poly2.wkt', 'poly3.wkt',
        #                                                                   'poly4.wkt', 'poly5.wkt', 'poly6.wkt',
        #                                                                   'poly7.wkt']}
        # geometries = {fname: load_wkt(data_path(fname)).wkb for fname in ['poly7.wkt']}

        simplifier = douglaspeucker
        simplifier_params = dict(epsilon=0.1)
        # self.save_shapefile(data_path('test'), 'orig', geometries)
        for mode in ["Expand", "Contract"]:
            print "*"*100, mode
            constraints = dict(expandcontract=mode,
                               # until I find a way to validate the constraint when receiving non-valid or non-simple
                               # polygons, I set these constraints so that I can use
                               # shapely.union and shapely.intersection to test expand/contract
                               prevent_shape_removal=True,
                               repair_intersections=True,
                               # to speedup repair intersections
                               use_topology=True,  # TODO: Fails with TRUE because multiple chains in linearring
                               simplify_shared_edges=True,
                               simplify_non_shared_edges=True,
                               )
            simp_geometries = self._test_geometry_simplification(geometries, simplifier, simplifier_params, constraints,
                                                                 check_valid=False, check_simple=False)
            # self.save_shapefile(data_path('test'), 'simp{}'.format(mode), simp_geometries)
            print "Validating geometries..."
            for key, simp_wkb in simp_geometries.iteritems():
                try:
                    geom = shapely.wkb.loads(geometries[key])
                    simp_geom = shapely.wkb.loads(simp_wkb)

                    # intersection = geom.intersection(simp_geom)
                    # union = geom.union(simp_geom)
                    if mode == "Expand":
                        # Nothing from the original geometry is lost
                        diff = geom.difference(simp_geom)
                        if diff.area > 1e-8:
                            raise self.failureException("Part of original geometry is lost")
                    if mode == "Contract":
                        diff = simp_geom.difference(geom)
                        if diff.area > 1e-8:
                            raise self.failureException("Part of simplified geometry is not in the original geometry")
                except Exception:
                    print "Failed on geometry id={}".format(key)
                    raise

    def test_expandcontract_edgecase1(self):
        """ Simplifying the following geometry fails when contracting/expanding with these constraints

        TODO: Transform the test into proper unit testing the ChainDB.apply_expandcontract function
        """
        geometries = {'A': load_wkb(data_path('mediterraneansea.txt'), hex=True).wkb}

        simplifier = douglaspeucker
        simplifier_params = dict(epsilon=0.01)
        for mode in ["Expand", "Contract"]:
            print "*"*100, mode
            constraints = dict(expandcontract=mode,
                               prevent_shape_removal=False,
                               prevent_shape_removal_min_points=3,
                               repair_intersections=True,
                               use_topology=False,
                               use_topology_snap_precision=0.0001,
                               simplify_non_shared_edges=False,
                               simplify_shared_edges=False,
                               )
            simp_geometries = self._test_geometry_simplification(geometries, simplifier, simplifier_params, constraints,
                                                                 check_valid=False, check_simple=False)
            print "Validating geometries..."
            self.assertEquals(len(simp_geometries), 1)
            for key, simp_wkb in simp_geometries.iteritems():
                try:
                    geom = shapely.wkb.loads(geometries[key])
                    simp_geom = shapely.wkb.loads(simp_wkb)
                    print len(geom), len(simp_geom)

                    # intersection = geom.intersection(simp_geom)
                    # union = geom.union(simp_geom)
                    if mode == "Expand":
                        # Nothing from the original geometry is lost
                        diff = geom.difference(simp_geom)
                        if diff.area > 1e-8:
                            raise self.failureException("Part of original geometry is lost")
                    if mode == "Contract":
                        diff = simp_geom.difference(geom)
                        if diff.area > 1e-8:
                            raise self.failureException("Part of simplified geometry is not in the original geometry")
                except Exception:
                    print "Failed on geometry id={}".format(key)
                    raise

    def assertSmallerGeometries(self, geometry, simp_geometry, threshold_min, threshold_max):
        size_orig = len(geometry)
        size_simp = len(simp_geometry)
        reduction = size_simp / float(size_orig)
        if not threshold_min <= reduction <= threshold_max:
            self.fail("Geometry's original size is %s and simplified size is %s. Expected %s-%s diff but got %s"
                      % (size_orig, size_simp, threshold_min, threshold_max, reduction))

    def test_repair_intersections(self):
        geometries = load_shapefile(data_path('naturalearth_nations/ne_10m_admin_0_countries.shp'),
                                    geom_key='ADM0_A3')
        simplifier = douglaspeucker
        simplifier_params = dict(epsilon=0.1)
        constraints = dict(repair_intersections=True)
        self._test_geometry_simplification(geometries, simplifier, simplifier_params, constraints,
                                           check_valid=True, check_simple=True)

    def test_repair_intersections_with_topology(self):
        geometries = load_shapefile(data_path('naturalearth_nations/ne_10m_admin_0_countries.shp'),
                                    geom_key='ADM0_A3')
        geometries = {i: wkb for i, wkb in geometries.iteritems() if i.split(":")[-1] in ["FRA", "ESP", "AND"]}

        simplifier = douglaspeucker
        simplifier_params = dict(epsilon=0.1)
        for simplify_shared_edges in (False, True):
            for simplify_non_shared_edges in (False, True):
                constraints = dict(repair_intersections=True,
                                   use_topology_snap_precision=0.0001,
                                   use_topology=True,
                                   simplify_shared_edges=simplify_shared_edges,
                                   simplify_non_shared_edges=simplify_non_shared_edges,
                                   )
                simp_geometries = self._test_geometry_simplification(geometries, simplifier, simplifier_params, constraints,
                                                                     check_valid=True, check_simple=True)
                for key in geometries.keys():
                    thresholds = 1.0, 1.0
                    if key.endswith("AND"):
                        if simplify_shared_edges:  # andorra is all shared frontier
                            thresholds = 0.01, 0.8
                    else:
                        if not simplify_non_shared_edges and simplify_shared_edges:
                            thresholds = 0.8, 1.0   # only spain-andorra-france frontier can be simplified
                        if simplify_non_shared_edges and simplify_shared_edges:
                            thresholds = 0.01, 0.5  # everything simplified
                        if simplify_non_shared_edges and not simplify_shared_edges:
                            thresholds = 0.01, 0.7  # everything except spain-adorra-france frontier
                    self.assertSmallerGeometries(geometries[key], simp_geometries[key], *thresholds)

    def test_line_first_and_last_segment_intersects_after_simplify(self):
        line_geom = load_wkt(data_path('line1.wkt'))
        simplifier = douglaspeucker
        simplifier_params = dict(epsilon=150)
        constraints = dict(repair_intersections=True)
        self._test_geometry_simplification(line_geom.wkb, simplifier, simplifier_params, constraints,
                                           check_valid=True, check_simple=True)

    def test_build_geometry(self):
        """ Test that build_geometry correctly merge chains
        """
        for num_points in range(3, 7):
            cdb = ChainDB()

            # generate a geometry
            points = [(x, x**2) for x in xrange(num_points*2)]
            gpoly = ogr.Geometry(ogr.wkbPolygon)
            gring = ogr.Geometry(ogr.wkbLinearRing)
            for p in points:
                gring.AddPoint_2D(*p)
            gring.AddPoint_2D(*points[0])  # close ring
            gpoly.AddGeometry(gring)
            wkb = gpoly.ExportToWkb(1)

            cdb.add_geometry('A', wkb)
            wkb2 = cdb.to_wkb('A')

            self.assertEquals(wkb, wkb2)

if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import unittest
from afcsimplifier.simplifier import ChainDB
from afcsimplifier.douglaspeucker import douglaspeucker
import shapely.wkt
import shapely.wkb
import shapely.validation
import ogr


def load_wkt(path):
    with open(path, 'r') as f:
        return shapely.wkt.load(f)


def load_shapefile(path, geom_key=None):
    # Get the driver
    driver = ogr.GetDriverByName('ESRI Shapefile')
    dataset = driver.Open(path, 0)

    layer = dataset.GetLayer()
    geometries = {}
    for index in xrange(layer.GetFeatureCount()):
        feature = layer.GetFeature(index)
        geometry = feature.GetGeometryRef()
        if geom_key is None:
            key = "g{}".format(index)
        else:
            key = "g{}:{}".format(index, feature.GetFieldAsString(geom_key))
        geometries[key] = geometry.ExportToWkb(1)
    return geometries


class TestCaseGeometry(unittest.TestCase):
    """ TestCase with utility functions to test geometry validity and simplicity.

        Valid and Simple definitions are guided by
        "OpenGIS Implementation Specification for Geographic information - Simple feature access - Part 1"
    """

    def simplify_geometries(self, geom_wkb_dict, simplifier, simplifier_params, constraints):
        """ Simplify a collection of geometries using afcsimplifier and a specific simplifier algorithm and constraints.
        :param geom_wkb_dict: dict (key, value) = (identifier, wkb (binary string))
        :param simplifier: simplify algorithm function (eg. douglaspeucker, visvalingam)
        :param simplifier_params: algorithm simplifier parameters (eg. for douglaspeucker, {'epsilon': 0.3})
        :param constraints: dict with constraints that will be set in ChainDB.set_constraints
        :return: Yields a tuple (identifier, simplified wkb) for every identifier in geom_wkb_dict.
        """
        cdb = ChainDB()
        for key, wkb in geom_wkb_dict.iteritems():
            cdb.add_geometry(key, wkb)
        cdb.set_constraints(**constraints)
        print "simplify all"
        cdb.simplify_all(simplifier=simplifier, **simplifier_params)
        print "simplified"
        for key in geom_wkb_dict.iterkeys():
            yield key, cdb.to_wkb(key)

    def simplify_geometry(self, wkb, *args, **kwargs):
        """ Same as simplify_geometries, but for a single geometry.
        :param wkb: wkb (binary string)
        :return: simplified wkb (binary string)
        """
        for key, wkb_simp in self.simplify_geometries({'A': wkb}, *args, **kwargs):
            return wkb_simp

    def assertValidGeometry(self, wkb):
        """ Asserts that the goemetry wkb (bin) is valid. """
        g = shapely.wkb.loads(wkb)
        if g.is_valid:
            return
        shapely.validation.explain_validity(g)
        raise self.failureException("Geometry is not valid")

    def assertInvalidGeometry(self, wkb):
        """ Asserts that the goemetry wkb (bin) is not valid. """
        g = shapely.wkb.loads(wkb)
        if not g.is_valid:
            return
        raise self.failureException("Geometry is valid")

    def assertSimpleGeometry(self, wkb):
        """ Asserts that the goemetry wkb (bin) is simple. """
        g = shapely.wkb.loads(wkb)
        if g.is_simple:
            return
        raise self.failureException("Geometry is not simple")

    def assertNonSimpleGeometry(self, wkb):
        """ Asserts that the goemetry wkb (bin) is not simple. """
        g = shapely.wkb.loads(wkb)
        if not g.is_simple:
            return
        raise self.failureException("Geometry is simple")

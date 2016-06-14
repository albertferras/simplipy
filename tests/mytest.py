#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from afcsimplifier.douglaspeucker import douglaspeucker
from afcsimplifier.simplifier import ChainDB
from utils import load_shapefile
from test_simplify import data_path


def run():
    data, key, epsilon = data_path('hrp00b11m/canada.shp'), 'HR_UID', 150
    data, key, epsilon = data_path('naturalearth_nations/ne_10m_admin_0_countries.shp'), 'ISO_A2', 0.05
    geom_wkb_dict = load_shapefile(data, geom_key=key)

    cdb = ChainDB()
    cdb.set_debug()
    for key, wkb in geom_wkb_dict.iteritems():
        cdb.add_geometry(key, wkb)

    constraints = dict(repair_intersections=True)
    simplifier = douglaspeucker
    simplifier_params = dict(epsilon=epsilon)
    cdb.set_constraints(**constraints)
    cdb.simplify_all(simplifier=simplifier, **simplifier_params)
    # for key in geom_wkb_dict.iterkeys():
    #     geom_wkb = cdb.to_wkb(key)
    #     print key, len(geom_wkb) if geom_wkb else None


def run2():
    data, key, epsilon = data_path('hrp00b11m/canada.shp'), 'HR_UID', 150
    data, key, epsilon = data_path('naturalearth_nations/ne_10m_admin_0_countries.shp'), 'ISO_A2', 0.05
    geom_wkb_dict = load_shapefile(data, geom_key=key)

    cdb = ChainDB()
    cdb.set_debug()
    for key, wkb in geom_wkb_dict.iteritems():
        cdb.add_geometry(key, wkb)

    constraints = dict(repair_intersections=True,
                       use_topology_snap_precision=0.0001,
                       use_topology=True,
                       simplify_shared_edges=True,
                       simplify_non_shared_edges=True)
    simplifier = douglaspeucker
    simplifier_params = dict(epsilon=epsilon)
    cdb.set_constraints(**constraints)
    cdb.simplify_all(simplifier=simplifier, **simplifier_params)
    # for key in geom_wkb_dict.iterkeys():
    #     geom_wkb = cdb.to_wkb(key)
    #     print key, len(geom_wkb) if geom_wkb else None


if __name__ == "__main__":
    run2()

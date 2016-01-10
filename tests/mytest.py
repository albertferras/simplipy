#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from afcsimplifier.douglaspeucker import douglaspeucker
from afcsimplifier.simplifier import ChainDB
from utils import load_shapefile
from test_simplify import data_path
from guppy import hpy; h=hpy()

def run():
    geom_wkb_dict = load_shapefile(data_path('hrp00b11m/canada.shp'), geom_key='HR_UID')
    print h.heap()
    print "-" * 10

    cdb = ChainDB()
    cdb.set_debug()
    for key, wkb in geom_wkb_dict.iteritems():
        cdb.add_geometry(key, wkb)

    print h.heap()
    print "-" * 10
    return

    constraints = dict(repair_intersections=True,
                       repair_intersections_precision=100.0)
    simplifier = douglaspeucker
    simplifier_params = dict(epsilon=150)
    cdb.set_constraints(**constraints)
    cdb.simplify_all(simplifier=simplifier, **simplifier_params)
    for key in geom_wkb_dict.iterkeys():
        print key, len(cdb.to_wkb(key))


if __name__ == "__main__":
    run()

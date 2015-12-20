#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from afcsimplifier.douglaspeucker import douglaspeucker
from utils import load_wkt, simplify_geometry


def run():
    constraints = dict(repair_intersections=True,
                       repair_intersections_precision=100.0)
    simplifier = douglaspeucker
    simplifier_params = dict(epsilon=150)
    line_geom = load_wkt('./data/line1.wkt')
    simp_wkb = simplify_geometry(line_geom.wkb, simplifier, simplifier_params, constraints)


if __name__ == "__main__":
    run()

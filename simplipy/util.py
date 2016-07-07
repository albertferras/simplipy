#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from collections import namedtuple

# POINT DATA STRUCT (coordinates + removed flag)
P_COORD = 0
P_REMOVED = 1


def to_points_data(geometry, is_exterior):
    points = tuple(geometry.coords)
    if geometry.type == 'LinearRing' and geometry.is_ccw != is_exterior:
        # if clockwise and exterior or counterclockwise and interior -> reverse points (as they should)
        points = reversed(points)
    return [[p, False] for p in points]

DIRECTION_NORMAL = 0
DIRECTION_REVERSE = 1


CGeometry = namedtuple('CGeometry', ['type', 'parent', 'children'])
CChain = namedtuple('CChain', ['parents', 'points'])
# a chain can have 1 or 2 parents (shared polygons). 1st parent has DIRECTION_NORMAL and 2nd DIRECTION_REVERSE

CSegment = namedtuple('CSegment', ['idx',  # index of this segment in the 'segment list'
                                   'chain_idx',  # chain_idx in the 'chains list'
                                   'points_idx',  # Two indexes in chains[chain_idx].points representing the segment
                                   ])


def is_closed_chain(points):
    return points[0][P_COORD] == points[-1][P_COORD]

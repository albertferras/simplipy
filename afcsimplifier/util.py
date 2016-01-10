'''
Created on Sep 6, 2013

@author: albert
'''
import itertools

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

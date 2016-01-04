#!/usr/bin/python -u
#encoding:utf-8

import geotool
from util import P_COORD, P_REMOVED


# determine if a point is inside a given polygon or not
# Polygon is a list of (x,y) pairs.
# source: http://www.ariel.com.au/a/python-point-int-poly.html
def point_inside_polygon(point, poly):
    x, y = point
    n = len(poly)
    inside = False

    p1x, p1y = poly[0][P_COORD]
    for i in range(n+1):
        p2x, p2y = poly[i % n][P_COORD]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside


def is_valid(segment, previous_segment, next_segment, expand=True):
    """ Returns true if simplified [segment] is correctly expanding or contracting
    :param segment: list of points. First and last points is the simplified segment.
                    Rest are points from the original geometry.
    :param previous_segment: previous segment of the simplified geometry (format: same as [segment])
    :param next_segment: next segment of the simplified geometry (format: same as [segment])
    :param expand: true for Expand, false for Contract
    :return:
    """
    if len(segment) < 3:
        return True

    # print "------------"
    # print "CHECK VALID prev", previous_segment[0][P_COORD], previous_segment[-1][P_COORD], len(previous_segment)
    # print "CHECK VALID cur", segment[0][P_COORD], segment[-1][P_COORD], len(segment)
    # print "CHECK VALID next", next_segment[0][P_COORD], next_segment[-1][P_COORD], len(next_segment)

    # 1 - Check that all points from the original geometry between the simplified segment points are
    # on one side of the simplified segment.
    # Expand: All points to the left or collinear
    # Contract: All points to the right or collinear
    pa = segment[0][P_COORD]
    pb = segment[-1][P_COORD]
    for p in segment[1:-1]:
        turn = geotool.ccw(pa, pb, p[P_COORD])
        # If removing this point made the polygon to expand/contract:
        # When expanding, every point in the original chain p0..pn must lay on the left side of segment p0,pn
        # When contracting, on the right side.
        if (turn < 0 and expand) or (turn > 0 and not expand):
            # Expand/Contract violation.
            return False

    # 2 - Even if all segments succeed in the previous check, we could still be violating the expand/contract
    # if a point from the previous or next segment lays inside the polygon [segment], which implies we would
    # have areas that were not part of the original polygon and areas that were part of the original polygon.
    # This means it would violate the expand/contract constraint.
    # To simplify computation time, we only check the simplified points of the prev/next segment AND
    # (in case of contract) the prev and next original point of [segment] in the original geometry.
    # Note: Assumes that if there was another point from any of the original points (prev/next segment) inside,
    #       it would be fixed by is_valid on those segments OR by RepairIntersection contraints.
    #       If not done this way, it will be computationally expensive to check it here.
    if expand:
        # Note: expanding only doesn't require this check (NOT COMPLETELY SURE!)
        return True

    points_to_check = [previous_segment[0][P_COORD], next_segment[-1][P_COORD]]
    if not expand:
        if len(previous_segment) > 2:
            points_to_check.append(previous_segment[-2][P_COORD])
        if len(next_segment) > 2:
            points_to_check.append(next_segment[1][P_COORD])

    if any(point_inside_polygon(p, segment) for p in points_to_check):
        return False
    return True


def fix(segment, expand=True):
    """ Fixes a simplified segment that is supposed to be expanding/contracting.

    Applies ConvexHull on it (TODO: IT MIGHT NOT FIX ANYTHING!)
    """
    side = -1 if expand else 1
    modified = False

    # recover points
    tmp = [0, 1]  # point indexes in segment of the new chain of points
    for k in xrange(len(segment)):
        tmp.append(k)
        while len(tmp) > 2 and geotool.ccw_norm(segment[tmp[-3]][P_COORD],
                                                segment[tmp[-2]][P_COORD],
                                                segment[tmp[-1]][P_COORD]) == side:
            tmp.pop(len(tmp)-2)
    for k in tmp:
        if segment[k][P_REMOVED]:
            modified = True
        segment[k][P_REMOVED] = False
    if not modified:
        raise Exception("Could not fix sorry")
    return modified

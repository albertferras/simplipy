'''
Created on Sep 6, 2013

@author: albert
'''
from util import P_REMOVED, P_COORD, to_points_data, DIRECTION_NORMAL, DIRECTION_REVERSE
import geotool


def douglaspeucker_rec(points, i, j, epsilon_squared):
    # point list must be CCW if exterior linearring
    # CW if interior linearring

    # Search point with biggest distance
    dmax = 0
    kmax = 0
    p0 = points[i]
    pn = points[j]

    k = i+1
    while k < j:
        p = points[k]
        if p[P_REMOVED] is False:
            d = geotool.perpendicular_qdistance(p[P_COORD], p0[P_COORD], pn[P_COORD])
            if d > dmax:
                kmax = k
                dmax = d
        k += 1
    # If distance is higher than epsilon, simplify recursively
    if (dmax > epsilon_squared):
        douglaspeucker_rec(points, i, kmax, epsilon_squared)
        douglaspeucker_rec(points, kmax, j, epsilon_squared)
    else:
        k = i+1
        while k < j:
            points[k][P_REMOVED] = True
            k += 1

def douglaspeucker(chain, epsilon=0.01):
    douglaspeucker_rec(chain, 0, len(chain)-1, epsilon**2)

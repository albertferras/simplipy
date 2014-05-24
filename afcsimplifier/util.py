'''
Created on Sep 6, 2013

@author: albert
'''

# POINT DATA STRUCT (coordinates + removed flag)
P_COORD = 0
P_REMOVED = 1

def to_points_data(points):
    # returns a list of [(x,y), is_removed]. Example: [(x,y), False]
    return [[p, False] for p in points]

DIRECTION_NORMAL = 0
DIRECTION_REVERSE = 1

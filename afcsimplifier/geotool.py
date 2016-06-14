'''
Created on Sep 6, 2013

@author: albert
'''

try:
    from geotool_c import (crosses, distance, qdistance, ccw, ccw_norm, count_line_chain_crossings, compute_allowed_shortcuts,
                           perpendicular_qdistance,
                           filter_edges_crossing_line, get_furthest_point, diameter, area)
    print "using C geotool"
except:
    from geotool_py import (crosses, distance, qdistance, ccw, ccw_norm, count_line_chain_crossings, compute_allowed_shortcuts,
                            perpendicular_qdistance,
                            filter_edges_crossing_line, get_furthest_point, diameter, area)
    print "using PY geotool"

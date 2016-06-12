from libcpp cimport bool as bool_t
from cpython cimport bool
from libc.math cimport abs as c_abs

cdef bint near(double a, double b, double atol=1e-8):
    return c_abs(a-b) < atol

cdef bint same_point(double px, double py, double qx, double qy):
    return near(px, qx) and near(py, qy)

cpdef bool crosses(double x1, double y1, double x2, double y2, double u1, double v1, double u2, double v2, bool endpoint_intersects=True):
    cdef double a, b, c, d, e, f, t, s
    cdef double denom

    if (same_point(x1, y1, u1, v1)
            or same_point(x1, y1, u2, v2)
            or same_point(x2, y2, u1, v1)
            or same_point(x2, y2, u2, v2)):
        return endpoint_intersects

    (a, b), (c, d) = (x2-x1, u1-u2), (y2-y1, v1-v2)
    denom = a*d - b*c
    if near(denom, 0):
        # parallel
        return False
    else:
        e, f = u1-x1, v1-y1
        t = (e*d - b*f)/denom
        s = (a*f - e*c)/denom
        # When 0<=t<=1 and 0<=s<=1 the point of intersection occurs within the
        # line segments
        if not endpoint_intersects:
            return 0 < t < 1 and 0 < s < 1
        else:
            return 0 <= t <= 1 and 0 <= s <= 1



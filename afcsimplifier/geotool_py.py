def near(a, b, atol=1e-8):
    return abs(a-b) < atol


def same_point(px, py, qx, qy):
    return near(px, qx) and near(py, qy)


def crosses(x1, y1, x2, y2, u1, v1, u2, v2, endpoint_intersects=True):
    """
    Return True if line segment line1 intersects line segment line2 and
    line1 and line2 are not parallel.

    (x1, y1), (x2, y2) = line1
    (u1, v1), (u2, v2) = line2
    """

    if (same_point(x1, y1, u1, v1)
            or same_point(x1, y1, u2, v2)
            or same_point(x2, y2, u1, v1)
            or same_point(x2, y2, u2, v2)):
        return endpoint_intersects

    (a, b), (c, d) = (x2-x1, u1-u2), (y2-y1, v1-v2)
    denom = float(a*d - b*c)
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

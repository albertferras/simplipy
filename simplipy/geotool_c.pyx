from libcpp cimport bool as bool_t
from cpython cimport bool
from libc.math cimport abs, asin, sqrt, atan2, M_PI



cdef bint near(double a, double b, double atol=1e-8):
    return abs(a-b) < atol

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


cdef double _qdistance(double x1, double y1, double x2, double y2):
    return (x1-x2)**2 + (y1-y2)**2


cpdef qdistance(double x1, double y1, double x2, double y2):
    return _qdistance(x1, y1, x2, y2)


cdef double _distance(double x1, double y1, double x2, double y2):
    return sqrt(_qdistance(x1, y1, x2, y2))


cpdef distance(double x1, double y1, double x2, double y2):
    return _distance(x1, y1, x2, y2)


cpdef perpendicular_qdistance(p, a, b):
    # source: http://stackoverflow.com/questions/849211/shortest-distance-between-a-point-and-a-line-segment
    # returns the perpendicular distance between point p and line ab
    cdef double px, py, ax, ay, bx, by, l2, t, proj_x, proj_y
    px, py = p
    ax, ay = a
    bx, by = b

    l2 = _qdistance(ax, ay, bx, by)
    if l2 == 0.0:
        return _qdistance(px, py, ax, ay)

    # dot product(p - a, b - a) / l2
    t = ((px - ax)*(bx - ax) + (py - ay)*(by - ay)) / l2
    if t < 0.0:
        return _qdistance(px, py, ax, ay)
    elif t > 1.0:
        return _qdistance(px, py, bx, by)

    proj_x = ax + t*(bx - ax)
    proj_y = ay + t*(by - ay)
    return _qdistance(px, py, proj_x, proj_y)


cpdef get_furthest_point(p, point_list):
    # Finds the point in point_list with maximum distance to p.
    # The result is the squared distance and the index of this point.
    cdef double dmax
    cdef int i, j
    cdef double px, py, ax, ay

    dmax = 0
    i = 0
    px, py = p
    for (j,  p2) in enumerate(point_list):
        ax, ay = p2
        d = _qdistance(px, py, ax, ay)
        if d > dmax:
            dmax = d
            i = j
    return dmax, i


def area(pa, pb, pc):
    return abs((pa[0] - pc[0]) * (pb[1] - pa[1]) - (pa[0] - pb[0]) * (pc[1] - pa[1]))


# Three points are a counter-clockwise turn if ccw > 0, clockwise if
# ccw < 0, and collinear if ccw = 0 because ccw is a determinant that
# gives the signed area of the triangle formed by p1, p2 and p3.
def ccw(o, a, b):
    # > 0 => left turn / ccw
    # = 0 => collinear
    # < 0 => right turn / cw
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def ccw_norm(o, a, b):
    """ ccw normalized to 3 values:
    1 when ccw(o, a, b) is positive (left turn)
    0 when ccw(o, a, b) is zero (collinear)
    -1 when ccw(o, a, b) is negative (right turn)
    """
    c = ccw(o, a, b)
    if c > 0:
        return 1
    elif c < 0:
        return -1
    else:
        return 0


def _keep_left(hull, r):
    while len(hull) > 1 and ccw(hull[-2], hull[-1], r) <= 0:
        hull.pop()
    if not len(hull) or hull[-1] != r:
        hull.append(r)
    return hull


def convex_hull(points):
    # Credit: https://gist.github.com/tixxit/242402
    # Graham scan
    points = sorted(points)
    l = reduce(_keep_left, points, [])
    u = reduce(_keep_left, reversed(points), [])
    return l.extend(u[i] for i in xrange(1, len(u) - 1)) or l


# The following hulls, rotatingCalipers and diameter is extracted from here:
# http://code.activestate.com/recipes/117225/
# convex hull (Graham scan by x-coordinate) and diameter of a set of points
# David Eppstein, UC Irvine, 7 Mar 2002
def hulls(points):
    """Graham scan to find upper and lower convex hulls of a set of 2d points."""
    U = []
    L = []
    points = sorted(points)  # create a new list in memory with the points sorted
    for p in points:
        while len(U) > 1 and ccw(U[-2], U[-1], p) <= 0:
            U.pop()
        while len(L) > 1 and ccw(L[-2], L[-1], p) >= 0:
            L.pop()
        U.append(p)
        L.append(p)
    return U, L


def rotatingCalipers(points):
    """Given a list of 2d points, finds all ways of sandwiching the points
between two parallel lines that touch one point each, and yields the sequence
of pairs of points touched by each pair of lines."""
    U, L = hulls(points)
    i = 0
    j = len(L) - 1
    while i < len(U) - 1 or j > 0:
        yield U[i], L[j]

        # if all the way through one side of hull, advance the other side
        if i == len(U) - 1:
            j -= 1
        elif j == 0:
            i += 1

        # still points left on both lists, compare slopes of next hull edges
        # being careful to avoid divide-by-zero in slope calculation
        elif (U[i+1][1]-U[i][1])*(L[j][0]-L[j-1][0]) > \
                (L[j][1]-L[j-1][1])*(U[i+1][0]-U[i][0]):
            i += 1
        else:
            j -= 1


def diameter(points):
    """Given a list of 2d points, returns the pair that's farthest apart."""
    # TODO: remove diameter computation (verify first)
    diam, pair = max([((p[0]-q[0])**2 + (p[1]-q[1])**2, (p, q))
                     for p, q in rotatingCalipers(points)])
    return pair


cdef double _angle_fix(double x):
    while x >= 2*M_PI:
        x -= 2*M_PI
    while x <= 0:
        x += 2*M_PI
    return x


cdef bool angle_is_between(double x, double a, double b):
    # returns True if x is between arc [a,b]
    x = _angle_fix(x)
    if a <= b:
        return a <= x <= b
    else:
        return x >= a or x <= b


cdef double angle(double px, double py, double qx, double qy):
    cdef double h, w
    h = qy - py
    w = qx - px
    return atan2(h, w)

to_rad = lambda d: d*M_PI/180.0
to_deg = lambda r: r*180.0/M_PI


def point_to_circle_tangent_angles(p, c, r):
    # given a point p and a circle with center c and radius r, returns the angles of the
    # 2 tangents of the circle that goes through p.
    px, py = p
    cx, cy = c
    alpha = asin(r/distance(px, py, cx, cy))
    beta = angle(px, py, cx, cy)

    (a, b) = (_angle_fix(beta-alpha), _angle_fix(beta+alpha))
    return a, b


cdef bool arc_intersection(double a, double b, double c, double d, double[2]& out):
    # returns the intersection of arc ab with arc cd
    cdef bool zab, zcd, case1, case2

    zab = (a > b)
    zcd = (c > d)
    if not zab and zcd:  # swap ab with cd so the code below isn't duplicated
        zab, zcd, a, b, c, d = zab, zcd, c, d, a, b

    if not zcd:
        if zab:
            case1 = c <= b
            case2 = d >= a
            if case1 and case2:
                raise Exception("Arc intersection results in 2 arcs!")
            elif case1:
                out[0] = c
                out[1] = b if b < d else d
                return True
            elif case2:
                out[0] = a if a > c else c
                out[1] = d
                return True
            else:
                return False  # empty intersection
        elif d < a or c > b:
            return False  # empty intersection
    out[0] = a if a > c else c
    out[1] = b if b < d else d
    return True


def filter_edges_crossing_line(G, C, line):
    # filter edges in graph G that intersects line
    (u1, v1), (u2, v2) = line

    i_list = G.keys()
    for i in i_list:
        j_list = G[i]

        x1, y1 = C[i]
        j_list = filter(lambda j: not crosses(x1, y1, C[j][0], C[j][1], u1, v1, u2, v2, endpoint_intersects=True), j_list)
        if len(j_list) == 0:
            G.pop(i)
        else:
            G[i] = j_list


cpdef compute_allowed_shortcuts(C, epsilon):
    # Chan & Chin '92 algorithm
    # Source: Compute-Allowed-Shortcuts in "A New Approach to Subdivision Simplification"
    # [Mark de Berg, Marc van Kreveld, Stefan Schirra;]
    # Input: a polygonal chain C with n vertices v1, ... vn and a real epsilon > 0.
    # Output: The set of all shortcuts of C
    # Notes:
    #  lij = half-line from vi to vj
    #  Dk = a closed disk centered at vk with radius epsilon
    cdef double I[2]
    cdef double qepsilon
    cdef bool open_arc
    cdef int i, j

    qepsilon = epsilon**2
    shortcuts = {}
    n = len(C)
    i = 0
    while i < n:
        open_arc = True
        I[0] = 0
        I[1] = 2*M_PI
        j = i + 1
        shortcuts_i = []
        while open_arc and j < n:
            ax, ay = C[i]
            bx, by = C[j]
            lij_angle = angle(ax, ay, bx, by)
            if angle_is_between(lij_angle, I[0], I[1]):
                shortcuts_i.append(j)
            if _qdistance(ax, ay, bx, by) > qepsilon:  # if vi not in Dj
                # intersect (a,b) with angles of half-lines that intersect Dj
                (da, db) = point_to_circle_tangent_angles(C[i], C[j], epsilon)
                open_arc = arc_intersection(I[0], I[1], da, db, I)
            j += 1
        if len(shortcuts_i) > 0:
            shortcuts[i] = shortcuts_i
        i += 1
    return shortcuts


def count_line_chain_crossings(line, chain):
    # count how many times the line(segment) crosses chain(list of segments)
    (x1, y1), (x2, y2) = line

    n = 0
    last_side = None
    for i in range(len(chain)-1):
        line2 = (chain[i], chain[i+1])
        side = ccw_norm(line[0], line[1], chain[i+1])

        (u1, v1), (u2, v2) = line2

        if crosses(x1, y1, x2, y2, u1, v1, u2, v2, endpoint_intersects=True) \
                and (0 != last_side != side != 0 or (last_side is None and side == -1)):
            n += 1
        if side != 0:
            last_side = side
        i += 1
    return n


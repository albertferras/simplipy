from osgeo import ogr

import shapely.wkb
import shapely.geometry

import geotool
from util import P_REMOVED, P_COORD, to_points_data, DIRECTION_NORMAL, DIRECTION_REVERSE
from visvalingam import visvalingam
from douglaspeucker import douglaspeucker
import expandcontract

import itertools
#import operator
import tools
import copy
import grid
import time
import progress

# GEOMETRY_TYPES = {
#     #0: "GeometryCollection",
#     1: "Point",
#     2: "LinearRing",
#     3: "Polygon",
#     #4: "MultiPoint",
#     #5: "MultiLineString",
#     6: "MultiPolygon",
#     #7: "GeometryCollection"
# }
#
# def get_geometry_type(geom):
#     return GEOMETRY_TYPES[geom.GetGeometryType()]

import sys
try:
    from shapely import speedups
    speedups.enable()
except:
    print "Couldn't enable shapely speedups. Ignoring"
    pass
# --------------------

from collections import Counter


class DataInconsistency(Exception):
    pass


def list_difference(l1, l2):
    c1 = Counter(l1)
    c2 = Counter(l2)
    diff = c1 - c2
    return list(diff.elements())

is_closed_chain = lambda points: points[0][P_COORD] == points[-1][P_COORD]


class ChainsSegment(object):
    SEGID_IDX = 0
    SEGID_CHAIN = 1
    SEGID_POINTS_IDX = 2

    SEGMENT_SEGID = 0
    SEGMENT_COORDS = 1

    def __init__(self, geometries, chains):
        self.geometries = geometries
        self.segments = []
        self.chains = chains
        grid_width = self.average_segment_length_sample(max_sample_size=100000)
        self.G = grid.Grid(width=grid_width)
        self._load_segments()

    def average_segment_length_sample(self, max_sample_size):
        """ Returns the average segment length from a sample of all segments in self.chains (from original geometry!)
        """
        distances = []
        try:
            for (c, chain) in enumerate(self.chains):
                if chain is None:
                    continue
                points = iter(chain[ChainDB.CHAIN_POINTS])
                last = next(points)[P_COORD]
                for p in points:
                    p = p[P_COORD]
                    if last != p:
                        dist = geotool.distance(p, last)
                        distances.append(dist)
                        if len(distances) > max_sample_size:
                            break
                    last = p
                if len(distances) > max_sample_size:
                    break
        except StopIteration:
            pass
        if len(distances) == 0:
            return 0.01
        avg = sum(distances) / len(distances)
        print "AVERAGE = {:.2f}".format(avg)
        return avg

    def _load_segments(self):
        for (c, chain) in enumerate(self.chains):
            if chain is None:
                continue
            points = chain[ChainDB.CHAIN_POINTS]
            first = None
            last = None
            is_closed = is_closed_chain(points)
            for (i, p) in enumerate(points):
                if p[P_REMOVED] is True:
                    continue
                if last is None:
                    first = i
                else:
                    self.new_segment(c, last, i)
                last = i
            if is_closed and (points[0][P_REMOVED] or points[-1][P_REMOVED]):
                # closed chain but first or last point was removed, so
                # we need to add an additional segment to close the chain
                self.new_segment(c, last, first)

    def get_segment_coordinates(self, seg_id):
        c = seg_id[self.SEGID_CHAIN]
        (i, j) = seg_id[self.SEGID_POINTS_IDX]
        chain_points = self.get_chain_points(c)
        return chain_points[i][P_COORD], chain_points[j][P_COORD]

    def is_consecutive_segments(self, seg_id1, seg_id2):
        """ Returns true if segments seg_id1,2 are from the same chain and are consecutive (touching endpoints)
        """
        # works if its the same chain only!
        c1 = seg_id1[self.SEGID_CHAIN]
        c2 = seg_id2[self.SEGID_CHAIN]
        if c1 == c2:
            # Segments come from the same chain, now check if they're consecutive
            points = self.get_chain_points(c1)
            (i1, j1) = seg_id1[self.SEGID_POINTS_IDX]
            (i2, j2) = seg_id2[self.SEGID_POINTS_IDX]
            if (points[i1][P_COORD] == points[j2][P_COORD]
                    or points[i2][P_COORD] == points[j1][P_COORD]):
                return True
        return False

    def new_segment(self, chain_idx, i, j):
        segment_idx = len(self.segments)
        seg_id = (segment_idx, chain_idx, (i, j))
        coords = self.get_segment_coordinates(seg_id)
        self.G.add(seg_id, coords)
        segment = (seg_id, coords)
        self.segments.append(segment)

    def get_chain_parent(self, chain_idx):
        return self.chains[chain_idx][ChainDB.CHAIN_PARENTS]

    def get_chain_points(self, chain_idx):
        return self.chains[chain_idx][ChainDB.CHAIN_POINTS]

    def get_segment_original_chain_coordinates(self, seg_id):
        chain_idx = seg_id[self.SEGID_CHAIN]
        (i, j) = seg_id[self.SEGID_POINTS_IDX]
        points = self.get_chain_points(chain_idx)
        if i < j:
            points = points[i:j+1]
        else:
            points = itertools.chain(points[i:], points[:j+1])
        result = map(lambda p: p[P_COORD], points)
        return result

    def recover_chain_points(self, seg_id, points_idx):
        chain_idx = seg_id[self.SEGID_CHAIN]
        sidx = seg_id[self.SEGID_IDX]
        (i, j) = seg_id[self.SEGID_POINTS_IDX]
        self.segments[sidx] = None  # Mark this segment as deleted
        chain_num_points = len(self.get_chain_points(chain_idx))
        k = i
        for l in points_idx[1:]:
            l = (l + i) % chain_num_points
            self.enable_point(chain_idx, l)
            self.new_segment(chain_idx, k, l)
            k = l
        if j != k:
            raise Exception("recover chain points failed")

    def is_sharing_chain_with_neighbour(self, seg_id1, seg_id2):
        c1 = seg_id1[self.SEGID_CHAIN]
        c2 = seg_id2[self.SEGID_CHAIN]

        chain1 = self.chains[c1]
        parents1 = chain1[ChainDB.CHAIN_PARENTS]
        return c1 == c2 and len(parents1) != 1

    def is_deleted_segment(self, seg_id):
        return self.segments[seg_id[self.SEGID_IDX]] is None

    def is_original_segment(self, seg_id):
        (i,j) = seg_id[self.SEGID_POINTS_IDX]
        return i == j-1

    def get_point(self, chain_idx, i):
        return self.get_chain_points(chain_idx)[i][P_REMOVED]

    def enable_point(self, chain_idx, i):
        self.get_chain_points(chain_idx)[i][P_REMOVED] = False



# point_key: use this to snap points that are almost identical
point_key = lambda p: ("%.5f;%.5f" % p[P_COORD])
# coord_key: should be the same as point_key! (not merging them due to performance)
coord_key = lambda coord: ("%.5f;%.5f" % coord)
point_key2 = lambda p, k: (int(p[P_COORD][0]/k)*k, int(p[P_COORD][1]/k)*k)
coord_key2 = lambda coord, k: (int(coord[0]/k)*k, int(coord[1]/k)*k)


class JunctionPoints(object):
    def __init__(self):
        self.junctions = {}

    def __len__(self):
        return len(self.junctions)

    def add_chain(self, key, chain_id):
        chains = self.junctions.get(key)
        if chains is None:
            self.junctions[key] = set()
        self.junctions[key].add(chain_id)

    def has_key(self, key):
        return self.junctions.has_key(key)

    def get(self, key):
        return self.junctions.get(key)


class ChainDB(object):
    KEY_SUBGEOMETRY = object()

    STARTING_POINT_FIRSTANDLAST = "firstandlast"
    STARTING_POINT_FIRSTANDFURTHEST = "firstandfurthest"
    STARTING_POINT_DIAMETERPOINTS = "diameterpoints"
    # Stores all geometry hierarchy (multipolygon->polygon->linearring->ring...) in a way
    # that we can access all chains in a quick way

    CHAIN_PARENTS = 0  # a chain can have 1 or 2 parents (shared polygons). 1st parent has DIRECTION_NORMAL and 2nd DIRECTION_REVERSE
    CHAIN_POINTS = 1

    GEOM_TYPE = 0
    GEOM_PARENT = 1
    GEOM_CHILDREN = 2

    def __init__(self):
        self.keys = {}          # (geom index, chain index)
        self.geometries = []    # (type, parent index, children indexes)
        self.chains = []        # lists of (geom parent, list of points)
        self.starting_points = self.STARTING_POINT_FIRSTANDFURTHEST
        self.set_constraints()

        try:
            self.max_iter = 5000 if len(sys.argv) <= 1 else int(sys.argv[1])
            self.max_fixes = 5000000 if len(sys.argv) <= 2 else int(sys.argv[2])
        except:
            self.max_iter = 5000
            self.max_fixes = 5000000
        self.DEBUG = False

    def set_debug(self):
        self.DEBUG = True

    def set_starting_points(self, mode):
        if mode not in [ChainDB.STARTING_POINT_FIRSTANDLAST,
                        ChainDB.STARTING_POINT_FIRSTANDFURTHEST,
                        ChainDB.STARTING_POINT_DIAMETERPOINTS]:
            raise Exception("Invalid starting points mode '%s'" % mode)
        self.starting_points = mode

    def set_constraints(self,
                        expandcontract=None,
                        repair_intersections=False,
                        prevent_shape_removal=None,
                        prevent_shape_removal_min_points=3,
                        use_topology=False,
                        use_topology_snap_precision=0.0001,
                        simplify_shared_edges=False,
                        simplify_non_shared_edges=False,
                        ):
        self.constraint_expandcontract = expandcontract
        self.constraint_shared_edges = simplify_shared_edges
        self.constraint_non_shared_edges = simplify_non_shared_edges
        self.constraint_repair_intersections = repair_intersections
        self.constraint_prevent_shape_removal = prevent_shape_removal
        self.constraint_prevent_shape_removal_min_points = prevent_shape_removal_min_points
        self.constraint_use_topology = use_topology
        self.constraint_use_topology_snap_precision = use_topology_snap_precision

    def get_keys(self):
        return self.keys

    def simplify_all(self, simplifier, **kwargs):
        self.simplify_keys(self.keys.keys(), simplifier, **kwargs)

    def simplify_keys(self, keys, simplifier, push_progress=None, **kwargs):
        self.junction_points = JunctionPoints()
        if self.constraint_use_topology:
            self.infer_topology()

        self.printchains = False
        if self.DEBUG:
            self.printchains = True and 0
        if self.printchains:
            self.print_geoms()
            self.print_chains(True)

        if push_progress:
            push_progress('Start')
        # 1 - simplify
        keys_found = []

        skip_shared_chains = False
        skip_non_shared_chains = False
        if self.constraint_use_topology:
            skip_shared_chains = not self.constraint_shared_edges
            skip_non_shared_chains = not self.constraint_non_shared_edges
            if self.constraint_expandcontract is not None:
                # A shared chain can never be simplified by expansion or contraction
                skip_shared_chains = True
            if self.constraint_repair_intersections:
                # A shared chain simplification will always be repaired because they always will have intersections
                # with other geometries
                skip_shared_chains = True

        for key in keys:
            keys_found.append(key)
            geom_idx = self.keys[key]
            for chain_id in self.get_chains_by_geom(geom_idx):
                chain = self.chains[chain_id]
                if chain is not None:
                    points = chain[self.CHAIN_POINTS]

                    is_shared_chain = len(chain[self.CHAIN_PARENTS]) > 1
                    if (is_shared_chain and skip_shared_chains) or (not is_shared_chain and skip_non_shared_chains):
                        continue

                    # if (self.constraint_use_topology is False
                    #     or (self.constraint_shared_edges and len(chain[self.CHAIN_PARENTS]) > 1)
                    #     or (self.constraint_non_shared_edges and len(chain[self.CHAIN_PARENTS]) == 1)):
                    simplifier(points, **kwargs)

        # 1.a - linearrings must have 4 points atleast (3 distinct)
        #     - linestring must have 2 distinct points atleast
        if self.constraint_prevent_shape_removal:
            if push_progress:
                push_progress("Preventing shape removal...",
                              "Preventing shape removal... (Please wait)")
            for key in keys_found:
                geom_idx = self.keys[key]
                self.prevent_shape_removal(geom_idx)

        # 2 - repair intersections and expand/contract constraint
        modified = True
        last_modified_by = None
        iteration = 0
        while modified:
            if self.DEBUG:
                print "\n\n=====CONSTRAINT ITERATION ", iteration, "===="
            if self.printchains:
                self.print_chains(True)
            iteration += 1
            modified = False

            # Repair Intersections
            modifier = 2
            if modifier != last_modified_by and self.constraint_repair_intersections:
                if push_progress:
                    push_progress('Repairing intersections... Iteration %s' % iteration,
                                  "Repairing intersections... (Please wait)")
                if self.repair_intersections(**kwargs):
                    if self.DEBUG:
                        print "REPAIRED INTERSECTIONS"
                    modified = True
                    last_modified_by = modifier
                    continue

            # Expand Contract constraint
            modifier = 1
            if modifier != last_modified_by and self.constraint_expandcontract is not None:
                if self.apply_expandcontract(self.constraint_expandcontract, keys_found):
                    if self.DEBUG:
                        print "FIXED EXPANDCONTRACT"
                    modified = True
                    last_modified_by = modifier
                    continue
            if self.DEBUG:
                print "ALL OK"
        if self.DEBUG:
            print "================================="
        if push_progress:
            push_progress('Done!', "Success!")
        if self.printchains:
            self.print_chains(True)

    def chain_shares_edges(self, chain_idx):
        chain = self.chains[chain_idx]
        return len(chain[self.CHAIN_PARENTS]) > 1

    def print_geoms(self):
        print "Geometries:"
        for (g, geom) in enumerate(self.geometries):
            print "%4d -> %16s : %6s : %s" % (g, geom[self.GEOM_TYPE], geom[self.GEOM_PARENT], geom[self.GEOM_CHILDREN])

    def paint_chains(self):
        for (c,chain) in enumerate(self.chains):
            if chain is None:
                continue

    def print_chains(self, show_points=False):
        print "chains:"
        for (c, chain) in enumerate(self.chains):
            if chain is None:
                print c, "->", "DELETED"
            else:
                points = chain[self.CHAIN_POINTS]
                is_closed = is_closed_chain(points)
                msg = "(closed)" if is_closed else ""
                print c, "->", chain[self.CHAIN_PARENTS], ":", id(points), len(points), "points", msg
                if show_points:
                    tab = "              "
                    i = 0
                    n = len(points)
                    while i < n:
                        start = i
                        while i < n and points[i][P_REMOVED]:
                            i += 1
                        if i - start > 0:
                            print tab, "     (REMOVED x{})".format(i - start)
                            # txt = "(DELETED)"
                            # pa = points[start][P_COORD]
                            # pb = points[i-1][P_COORD]
                            # print tab, "{:<10}[{:>3}:{:>3}] {}, {} -> {}, {}".format(txt, start, i, *(pa+pb))
                        while i < n and not points[i][P_REMOVED]:
                            p = points[i][P_COORD]
                            txt = "[q {}]".format(len(points) - i - 1)
                            print tab, "{:<10}[{:>3}] {}, {}".format(txt, i, *p)
                            i += 1

    def infer_topology(self):
        debug = False
        if debug:
            self.print_geoms()
            self.print_chains()

        K = self.constraint_use_topology_snap_precision
        # Identify junctions between chains
        # http://bost.ocks.org/mike/topology/ (Step 2.Join)
        # 1 - Map points
        point_map = {}  # may crash memory
        for (c, chain) in enumerate(self.chains):
            for point in chain[self.CHAIN_POINTS]:
                key = point_key2(point, K)
                geoms = point_map.get(key)
                if geoms is None:
                    point_map[key] = [c]
                else:
                    point_map[key].append(c)

        # 2 - Detect junctions
        for (c, chain) in enumerate(self.chains):
            points = chain[self.CHAIN_POINTS]
            last_key = point_key2(points[0], K)
            last_group = point_map.get(last_key)
            for p in points[1:]:
                key = point_key2(p, K)
                group = point_map.get(key)
                if group != last_group:
                    join = list_difference(group, last_group)
                    leaves = list_difference(last_group, group)
                    if len(join) > 0:
                        self.junction_points.add_chain(key, c)
                    if len(leaves) > 0:
                        self.junction_points.add_chain(last_key, c)
                    last_group = group
                last_key = key

        # 3 - Split chains by junction
        junction_to_junction = {}

        def mark_junction_to_junction_chain(key1, key2, chain_idx):
            L = junction_to_junction.get((key1,key2))
            if L is None:
                junction_to_junction[(key1, key2)] = [chain_idx]
            else:
                junction_to_junction[(key1, key2)].append(chain_idx)

        def _get_j2j_chain(key1, key2, chain_points):
            chain_idxs_marked = junction_to_junction.get((key1, key2))
            if chain_idxs_marked is not None:
                for chain_idx2 in chain_idxs_marked:
                    # verify that it's the same chain
                    p1 = chain_points
                    p2 = self.chains[chain_idx2][self.CHAIN_POINTS]

                    if point_key2(p1[0], K) != point_key2(p2[0], K) or point_key2(p1[-1], K) != point_key2(p2[-1], K):
                        raise Exception("this cant happen (j2j)")

                    if point_key2(p1[1], K) == point_key2(p2[1], K):
                        return chain_idx2
            return None

        def get_junction_to_junction_chain(key1, key2, chain_points):
            direction = DIRECTION_NORMAL
            chain_idx2 = _get_j2j_chain(key1, key2, chain_points)
            if chain_idx2 is None:
                direction = DIRECTION_REVERSE
                chain_idx2 = _get_j2j_chain(key2, key1, chain_points[::-1])
            return direction, chain_idx2

        disable_chains = set()
        for geom in self.geometries:
            if geom[self.GEOM_TYPE] != "LinearRing":
                continue
            if debug:
                print "---------------------"
                print "Geom %s" % geom[self.GEOM_PARENT]
            geom_chains = geom[self.GEOM_CHILDREN]

            new_chain_indexes = []
            chain_created = False
            for c in geom_chains:
                if debug:
                    print "CHAIN %s (parent=%s)" % (c, self.chains[c][self.CHAIN_PARENTS])
                    tab = "    "
                disable_chain = True
                chain = self.chains[c]
                parents = chain[self.CHAIN_PARENTS]
                if len(parents) != 1:
                    raise Exception("expecting parents size = 1!?")
                points = chain[self.CHAIN_POINTS]
                start_key = point_key2(points[0], K)

                i = 0
                j = 1
                while j < len(points):
                    p = points[j]
                    key = point_key2(p, K)
                    if self.junction_points.has_key(key):

                        subchain = points[i:j+1]
                        (direction, chain_idx2) = get_junction_to_junction_chain(start_key, key, subchain)

                        if debug:
                            print tab, "start_key=%s -> %s" % (start_key, key)
                            print tab, "Chain %s----->%s" % (list(self.junction_points.get(start_key)),
                                                             list(self.junction_points.get(key)))

                        # check if junction to junction A->B->A
                        if chain_idx2 is not None:
                            if self.chains[chain_idx2][self.CHAIN_PARENTS] == self.chains[c][self.CHAIN_PARENTS]:
                                chain_idx2 = None

                        if chain_idx2 is None:
                            # Subchain not yet saved
                            if j == len(points)-1 and chain_created is False:
                                # if last point in the chain but there was no junction inbetween
                                # no need to create new chain
                                chain_idx2 = c
                                dbg = "nochange"
                                disable_chain = False
                            else:
                                chain_created = True
                                # create new chain
                                chain_idx2 = len(self.chains)
                                self.chains.append(([parents[0]], subchain))
                                dbg = "new"
                            mark_junction_to_junction_chain(start_key, key, chain_idx2)
                        else:
                            chain_created = True
                            # two chains from distinct polygons will share the memory space
                            # subchain = self.chains[chain_idx2][self.CHAIN_POINTS]
                            dbg = "reused %s" % chain_idx2

                            self.chains[chain_idx2][self.CHAIN_PARENTS].append(parents[0])

                            # chain_idx2 = len(self.chains)
                            # self.chains.append((chain[self.CHAIN_PARENTS], direction, subchain))
                            # Subchain already saved
                        new_chain_indexes.append(chain_idx2)
                        if debug:
                            print tab, "SPLIT %s to chainid=%s" % (c, chain_idx2), dbg
                        i = j
                        start_key = key
                    j += 1
                if disable_chain:
                    disable_chains.add(c)
            if debug:
                print "geom new chains=%s" % new_chain_indexes

            if len(new_chain_indexes) > 0:
                parents = chain[self.CHAIN_PARENTS]
                for parent in parents:
                    geom = self.geometries[parent]
                    geom[self.GEOM_CHILDREN] = new_chain_indexes

            for c in disable_chains:
                self.chains[c] = None

        # 4 - Share chains
        # print_chains()
        if debug:
            self.print_geoms()
            self.paint_chains()

    def is_connected_by_junction(self, line1, line2, tolerance=0.01):
        key1a = coord_key2(line1[0], tolerance)
        key1b = coord_key2(line1[-1], tolerance)
        key2a = coord_key2(line2[0], tolerance)
        key2b = coord_key2(line2[-1], tolerance)

        if (key1a == key2a or key1a == key2b) and self.junction_points.has_key(key1a):
            return True
        if (key1b == key2a or key1b == key2b) and self.junction_points.has_key(key1b):
            return True
        return False

    def apply_expandcontract(self, mode, keys):
        """ Apply expand contract constraint to geometries in this ChainDB

        Works only for LinearRings (atleast 3 segments)

        :param mode: 'Expand' or 'Contract'
        :param keys: List of geometry keys to be applied
        :return:
        """
        # Find side (-1 or 1, result of ccw_norm)
        if mode == 'Expand':
            expand = True
        elif mode == "Contract":
            expand = False
        else:
            raise Exception("Invalid expandcontract mode: %s" % mode)

        any_modified = False
        for key in keys:
            geom_idx = self.keys[key]
            for part_geom_idx in self.find_parts_with_chains(geom_idx):
                modified = True
                while modified:
                    modified = False
                    # print "====" * 10
                    # print "GeomIDX=", part_geom_idx
                    # print "Segments:"
                    # for segment in self.get_simplified_segments(part_geom_idx):
                    #     print segment[0][P_COORD], segment[-1][P_COORD]
                    segments = self.get_simplified_segments(part_geom_idx)
                    sfirst = sa = segments.next()
                    ssecond = sb = segments.next()
                    for sc in segments:
                        if not expandcontract.is_valid(sb, previous_segment=sa, next_segment=sc, expand=expand):
                            modified |= expandcontract.fix(sb, expand=expand)
                        sa, sb = sb, sc
                    if not expandcontract.is_valid(sb, previous_segment=sa, next_segment=sfirst, expand=expand):
                        modified |= expandcontract.fix(sb, expand=expand)
                    if not expandcontract.is_valid(sfirst, previous_segment=sb, next_segment=ssecond, expand=expand):
                        modified |= expandcontract.fix(sfirst, expand=expand)
                    any_modified |= modified
        return any_modified

    def iter_chain_points(self, geom_idx):
        """ Iterate every point of chains a geom_idx in the correct order.

        Does not return consecutive identical points unless they're the first and last one of the full list of points.
        """
        geom = self.geometries[geom_idx]
        chain_ids = geom[self.GEOM_CHILDREN]

        last_p = None
        for chain_id in chain_ids:
            chain = self.chains[chain_id]
            points = chain[self.CHAIN_POINTS]

            # If chain is stored in reverse order (multiple parents, shared edges)
            parents = chain[self.CHAIN_PARENTS]
            if len(parents) == 2 and parents[1] == geom_idx:
                points = reversed(points)
            else:
                points = iter(points)

            # Yield first point only if it's different from the previous chain
            p = points.next()
            if last_p != p:
                yield p

            for p in points:
                yield p
            last_p = p

    def get_simplified_segments(self, geom_idx):
        points_iter = self.iter_chain_points(geom_idx)

        # Find first non-removed point
        first_point = points_iter.next()
        if first_point[P_REMOVED]:
            p = None
            first_half_segment = []
            for p in points_iter:
                first_half_segment.append(p)
                if not p[P_REMOVED]:
                    break
        else:
            p = first_point
            first_half_segment = [p]

        # At this point:
        # p = first non-removed point
        # first_filtered_points = list of points filtered before point p
        #                         (will be returned in last segment if points_iter are a closed chain)
        segment = [p]
        for p in points_iter:
            segment.append(p)
            if not p[P_REMOVED]:
                yield segment
                segment = [p]

        # At this point:
        # p = last point of all chains points
        # segment = list of points, starting at last non-removed point.

        # If original chain is closed, must return an additional segment to close the segments returned
        if first_point[P_COORD] == p[P_COORD] and (len(segment) + len(first_half_segment) > 2):
            segment += first_half_segment
            yield segment

    def find_parts_with_chains(self, geom_idx):
        # TODO: same as _get_line_primitives?!
        """ Yields all geom_idx's parts (children geom_idx) with chains

        Example:
        A multipolygon with 3 polygons and 2 rings each, will return one geom_idx for every linearring (total=6)
        A linearring or linestring will return one geom_idx in total

        :param geom_idx: index in self.geometries
        :return: list of geom_idx with chains
        """
        geom = self.geometries[geom_idx]
        geom_type = geom[self.GEOM_TYPE]
        if geom_type is None:
            return
        elif geom_type == "LinearRing" or geom_type == "LineString":
            yield geom_idx
        else:
            tmp = (self.find_parts_with_chains(child_geom_idx) for child_geom_idx in geom[self.GEOM_CHILDREN])
            for geom_idx2 in itertools.chain(*tmp):
                yield geom_idx2

    def repair_intersections(self, **kwargs):
        repaired = False
        tstart = time.time()
        cs = ChainsSegment(self.geometries, self.chains)
        if self.DEBUG:
            print "ChainsSegment build time = %.2f" % (time.time() - tstart)
            print "ChainsSegment total segments = %s" % len(cs.segments)

        iter_k = 0
        iterations = 0

        epsilon = kwargs.get('epsilon', 0.01)
        while iterations <= self.max_iter and iter_k < len(cs.segments):
            debug = (iterations == self.max_iter)
            #debug = True
            if debug:
                t = time.time()
                print "Iteration %s" % iterations

            iter_k_next = len(cs.segments)

            self._iteration = iterations

            repaired |= self._repair_intersections(cs, iter_k, epsilon, debug)
            iter_k = iter_k_next
            iterations += 1

            if debug:
                print "iteration time = %.2f" % (time.time() - t)
        if self.DEBUG:
            print "Total time = %.2f" % (time.time() - tstart)
        return repaired

    def _repair_intersections(self, cs, iter_k, epsilon, debug=False):
        if debug:
            print "repair:", iter_k, epsilon
        # returns true if a point was recovered, false otherwise
        repaired = False
        stop = False
        fix_count = 0
        # Find Intersections
        t = time.time()
        intersections = []
        while iter_k < len(cs.segments):
            s1 = cs.segments[iter_k]
            iter_k += 1
            if s1 is None:  # original or fixed segments doesn't have to be checked
                continue
            seg_id = s1[ChainsSegment.SEGMENT_SEGID]
            # print ">>> check intersections", seg_id
            #if is_original_segment(seg_id):
            #    continue
            line1 = cs.get_segment_coordinates(seg_id)

            # dbg = seg_id[ChainsSegment.SEGID_POINTS_IDX] in ((34, 35), (21, 32))
            # if dbg:
            #     print "====="
            #     print seg_id
            for seg_id2 in cs.G.hit(line1):
                # if dbg:
                #     print "\t", seg_id2
                if seg_id == seg_id2:
                    continue
                if cs.is_consecutive_segments(seg_id, seg_id2):
                    # Consecutive segments

                    # If lines are collinear, delete common endpoint to save 1 point and avoid self-intersection
                    line2 = cs.get_segment_coordinates(seg_id2)
                    p, q = line1
                    r, s = line2
                    ccw = geotool.ccw(q, p, r) if p == s else geotool.ccw(p, q, s)
                    if ccw == 0:  # If collinear
                        intersections.append((seg_id, seg_id2))
                    continue
                if cs.is_deleted_segment(seg_id2):
                    continue
                if cs.is_sharing_chain_with_neighbour(seg_id, seg_id2):
                    continue
                # don't compare 2 segments twice or a segment with itself
                if seg_id > seg_id2 or cs.is_original_segment(seg_id2):
                    line2 = cs.get_segment_coordinates(seg_id2)
                    if geotool.crosses(line1, line2, endpoint_intersects=True) and not self.is_connected_by_junction(line1, line2, tolerance=self.constraint_use_topology_snap_precision):
                        if debug:
                            print "INTERSECTION:", seg_id, seg_id2
                        intersections.append((seg_id, seg_id2))
        if debug:
            print "Find intersections time = %.2f" % (time.time() - t)
            print len(intersections), "intersections found"

        # apply SD heuristic
        for (segA_id, segB_id) in intersections:
            if debug:
                print "fix int:", segA_id, segB_id
            sa = cs.segments[segA_id[0]]
            sb = cs.segments[segB_id[0]]

            lineA = cs.get_segment_coordinates(segA_id)
            lineB = cs.get_segment_coordinates(segB_id)

            if sa is None or sb is None:  # If this intersection was fixed in a previously iteration
                if debug:
                    print "Skip %s %s" % (sa, sb)
                continue

            if debug:
                if fix_count >= self.max_fixes:
                    continue
                fix_count += 1

            # select the segment s that has an odd number of crossings with the spanning (original) chain C(s').
            # s is an original segment (no points in C(s) were removed)
            # One can prove that exactly one of {s, s'} has an odd number of crossings with the other's spanning chain.
            Ca = cs.get_segment_original_chain_coordinates(segA_id)
            Cb = cs.get_segment_original_chain_coordinates(segB_id)
            crossings_a = geotool.count_line_chain_crossings(lineA, Cb)
            crossings_b = geotool.count_line_chain_crossings(lineB, Ca)

            if crossings_a%2 == 1:
                C, Cp, s, sp, lineS, lineSP = Ca, Cb, sa, sb, lineA, lineB
            else:
                C, Cp, s, sp, lineS, lineSP = Cb, Ca, sb, sa, lineB, lineA

            if crossings_a == crossings_b == 0:
                if debug:
                    print "no crossings?!"
                continue

            # This check is to avoid infinite loops
            # The idea here is that C has only 2 points, there is no
            # possible point to set as enabled in C again.
            # This can happen when the original non-simplified polygon has self-intersections
            # or intersections with another chain
            if len(C) == 2:
                if len(Cp) > 2:
                    C, Cp = Cp, C
                    s, sp = sp, s
                    lineS, lineSP = lineSP, lineS
                else:
                    # never check this again. intersection can't be fixed
                    if debug:
                        print "Unfixable %s %s" % (sa, sb)
                    continue

            # Construct detour graph, G(s), corresponding to s.
            # The vertices of G(s) are the vertices of the spanning chain C(s), and two vertices are
            # joined by an edge in G(s) if and only if the corresponding line segment is e-feasible and does
            # not intersect s'.
            # Note: Since the function compute_allowed_shortcuts is O(n^2), it may take a lot of time to call
            # the function if there are too many points in C. To avoid slow calls, we will simplify this subchain with
            # a lower tolerance.

            if len(C) < 500:
                if debug:
                    t = time.time()
                allowed_shortcuts = geotool.compute_allowed_shortcuts(C, epsilon)
                if debug:
                    print "AllShortCuts = %.3f (%s points)" % (time.time() - t, len(C))
                # filter edges in graph G that intersect s'
                geotool.filter_edges_crossing_line(allowed_shortcuts, C, lineSP)
                # Find shortest path in detour-graph
                shortest_path = tools.shortest_path_dag_ordered(allowed_shortcuts, 0, len(C)-1)
            else:
                shortest_path = None

            if shortest_path is not None:
                if debug:
                    print "Fix SGD %s %s" % (sa[ChainsSegment.SEGMENT_SEGID],
                                             sb[ChainsSegment.SEGMENT_SEGID])
                    print "shortest path:", shortest_path
                cs.recover_chain_points(s[ChainsSegment.SEGMENT_SEGID], shortest_path)
                repaired = True
            else:
                if debug:
                    print "Fix Rand %s %s" % (sa, sb)
                # Shortest path not found. Select random vertex from C(s) and C(s')
                # Instead of random, we select the vertex in the middle(array length) of each chain.
                # if debug:
                #     print "COULDNT FIND SHORTEST PATH! MUST IMPLEMENT ALTERNATIVE"
                # shortest_path = range(len(C))
                Cn = len(C)
                Cpn = len(Cp)
                # TODO: dont recover a point which create a intersection!
                if Cn > 2:
                    cs.recover_chain_points(s[ChainsSegment.SEGMENT_SEGID], [0, Cn/2, Cn-1])
                    repaired = True
                if Cpn > 2:
                    cs.recover_chain_points(sp[ChainsSegment.SEGMENT_SEGID], [0, Cpn/2, Cpn-1])
                    repaired = True
        return repaired

    def add_geometry(self, key, wkb):
        try:
            geometry = shapely.wkb.loads(wkb)
        except:
            print "Couldn't import geometry [{}], ignoring".format(key)
            import traceback
            traceback.print_exc()
            geometry = None
            raise

        self.keys[key] = None # geom index
        i = self._add_geometry(key, geometry)
        if i is None:
            raise Exception("Invalid geometry [key='%s']" % key)
        self.keys[key] = i
        del geometry

    def _add_geometry(self, key, geometry, parent=None, **kwargs):
        if geometry is not None:
            item = [geometry.type, parent, None]  # 0=type, 1=parent(index), 2=children(index)
        else:
            item = [None, parent, None]

        i = len(self.geometries)  # index of 'this geometry' (parent for children)
        self.geometries.append(item)

        if geometry is None:
            return i
        elif geometry.type in ["MultiPolygon", "MultiLineString"]:
            children = [self._add_geometry(key, poly, parent=i, **kwargs) for poly in geometry.geoms]
        elif geometry.type == 'Polygon':
            children = []
            c = self._add_geometry(key, geometry.exterior, parent=i, is_exterior=True, **kwargs)
            children.append(c)

            for interior in geometry.interiors:
                c = self._add_geometry(key, interior, parent=i, is_exterior=False, **kwargs)
                children.append(c)
        elif geometry.type == 'LinearRing':
            children = []
            points = self.linearring_to_point_list(geometry, is_exterior=kwargs['is_exterior'])
            chain_data = ([i], to_points_data(points))  # (parents (this ring), list of points)
            self.chains.append(chain_data)
            c = len(self.chains)-1
            children.append(c)
        elif geometry.type == "LineString":
            children = []
            points = list(geometry.coords)
            chain_data = ([i], to_points_data(points))
            self.chains.append(chain_data)
            c = len(self.chains)-1
            children.append(c)
        else:
            raise Exception("Not supported geometry type: %s" % geometry.type)
        item[2] = children
        return i

    def linearring_to_point_list(self, geometry, is_exterior=True):
        # Exterior LinearRing points orientation must be counterclockwise
        # Interior LinearRing points orientation must be clockwise
        point_list = list(geometry.coords)
        if geometry.is_ccw != is_exterior:
            # if clockwise and exterior or counterclockwise and interior -> reverse points (as they should)
            point_list = point_list[::-1]
        return point_list

    def split_chain(self, point_list):
        # each point list includes the first and last point of the next point list.
        # example: p1,p2,...p20
        # output:
        # p1..p4, p4..p15, p15..p20
        # Choose starting points (check parameters)
        if self.starting_points == ChainDB.STARTING_POINT_FIRSTANDLAST:
            i = len(point_list)-2
            yield point_list[:i+1]
            yield point_list[i:]
        elif self.starting_points == ChainDB.STARTING_POINT_FIRSTANDFURTHEST:
            p = point_list[0]
            (qdist, i) = geotool.get_furthest_point(p, point_list)
            yield point_list[:i+1]
            yield point_list[i:]
        elif self.starting_points == ChainDB.STARTING_POINT_DIAMETERPOINTS:
            (p, q) = geotool.diameter(point_list)
            i = point_list.index(p)
            j = point_list.index(q)
            if j < i: j, i = i, j
            yield point_list[i:j+1]
            yield point_list[j:] + point_list[:i]
        else:
            yield point_list

    def prevent_shape_removal(self, geom_idx):
        for child_geom_idx in self._get_line_primitives(geom_idx):
            self.fix_line_if_not_enough_points(child_geom_idx, self.constraint_prevent_shape_removal_min_points)

    def _get_line_primitives(self, geom_idx):
        """ Returns geom_idx for linestrings and linearrings in geometry [geom_idx]"""
        geom = self.geometries[geom_idx]
        gtype = geom[self.GEOM_TYPE]
        if gtype == "LinearRing" or gtype == "LineString":
            yield geom_idx
        else:
            for children_geom_idx in geom[self.GEOM_CHILDREN]:
                for ring_geom_idx in self._get_line_primitives(children_geom_idx):
                    yield ring_geom_idx

    def fix_line_if_not_enough_points(self, geom_idx, min_points=3):
        """ Recover points from a simplified geometry (geom_idx) to have atleast [min_points] distinct points.
        Works only if geom_idx is a LinearRing or LineString.
        """
        num_points = 0
        original_num_points = 0
        chains = self.get_chains_by_geom(geom_idx)
        geom = self.geometries[geom_idx]

        # Check if line is a closed chain
        first_point = self.chains[chains[0]][self.CHAIN_POINTS][0]
        last_point = self.chains[chains[-1]][self.CHAIN_POINTS][-1]
        closed_chain = (first_point[P_COORD] == last_point[P_COORD])

        # Get all points of the ring
        last_simp_p = None
        last_orig_p = None
        for p in self.iter_chain_points(geom_idx):
            if p[P_REMOVED]:
                if last_orig_p != p:
                    original_num_points += 1
                last_orig_p = p
            else:
                if last_simp_p != p:
                    num_points += 1
                last_simp_p = p

        if closed_chain:
            if not first_point[P_REMOVED] and not last_point[P_REMOVED]:
                # Was counted twice
                num_points -= 1
                original_num_points -= 1

            if num_points < min_points:
                # Closed chains must remain closed
                first_point[P_REMOVED] = False
                last_point[P_REMOVED] = False
                if first_point[P_REMOVED] and last_point[P_REMOVED]:
                    # Update num distinct points
                    num_points += 1

        # If not enough points, simplify again using visvalingam until MIN_POINTS is reached when possible
        if num_points < min_points:
            # Check if any part of the chain is shared for multiple geometries (when using topology)
            shares_edge = any([self.chain_shares_edges(chain_idx) for chain_idx in chains])
            if not shares_edge and closed_chain:
                # use visvalingam to simplify the whole ring
                pointsdata_list = list(self.iter_chain_points(geom_idx))
                for p in pointsdata_list:
                    p[P_REMOVED] = False
                visvalingam(pointsdata_list, minArea=99999, ring_min_points=min_points)

                # Closed linestrings must remain closed
                if geom[self.GEOM_TYPE] == "LineString":
                    first_point[P_REMOVED] = False
                    last_point[P_REMOVED] = False
            # Not allowed to do polygon simplification
            elif num_points < min_points:
                # Recover "random" point (TODO: IMPROVE THIS. MAYBE USE VISVALINGAM IN SOME WAY)
                recover_points = (min_points - num_points)
                delta = (original_num_points - num_points) / recover_points
                # Unflag as deleted one point for every [delta] points
                # This will flag [recover_points] points
                cnt = delta / 2  # start counting at [delta/2] to unflag middle points
                for chain_id in chains:
                    points = self.chains[chain_id][self.CHAIN_POINTS]
                    for p in points:
                        if not p[P_REMOVED]:
                            continue
                        cnt += 1
                        if cnt < delta:
                            continue
                        p[P_REMOVED] = False
                        num_points += 1
                        cnt = 0

    def fix_ring_if_not_enough_points(self, ring_geom_idx, min_points=3):
        num_points = 0
        chains = self.get_chains_by_geom(ring_geom_idx)

        # Get all points of the ring
        for chain_id in chains:
            points = self.chains[chain_id][self.CHAIN_POINTS]
            chain_size = len(filter(lambda p: p[P_REMOVED] is False, points))
            num_points += chain_size

        # If not enough points, simplify again using visvalingam until MIN_POINTS is reached when possible
        if num_points <= min_points:
            ring_shares_edge = any([self.chain_shares_edges(chain_idx) for chain_idx in chains])
            if not ring_shares_edge:
                # use visvalingam to simplify the whole ring
                pointsdata_list = []
                for chain_id in chains:
                    pointsdata_list.extend(self.chains[chain_id][self.CHAIN_POINTS])
                for p in pointsdata_list:
                    p[P_REMOVED] = False
                visvalingam(pointsdata_list, minArea=99999, ring_min_points=min_points)
            elif num_points < min_points:
                # Recover "random" point
                for chain_id in chains:
                    points = self.chains[chain_id][self.CHAIN_POINTS]
                    for p in points:
                        if p[P_REMOVED] is True:
                            p[P_REMOVED] = False
                            num_points += 1
                            if num_points >= min_points:
                                return

    def get_chains_by_geom(self, geom_idx):
        geom = self.geometries[geom_idx]
        if geom[self.GEOM_TYPE] is None:
            return []
        elif geom[self.GEOM_TYPE] in ["LinearRing", 'LineString']:
            chain_ids = geom[self.GEOM_CHILDREN]
            return chain_ids
        elif geom[self.GEOM_TYPE] in ['Polygon', 'MultiPolygon', 'MultiLineString']:
            return reduce(lambda a, b: a+b, map(self.get_chains_by_geom, geom[self.GEOM_CHILDREN]))
        else:
            raise NotImplemented("get_chains_by_geom not implemented for {}".format(geom[self.GEOM_TYPE]))

    def _build_geometry(self, geom_idx):
        (gtype, parent, children) = self.geometries[geom_idx]
        if gtype is None:
            return None
        elif gtype in ["MultiPolygon", "MultiLineString"]:
            if gtype == "MultiPolygon":
                geom = ogr.Geometry(ogr.wkbMultiPolygon)
            else:
                geom = ogr.Geometry(ogr.wkbMultiLineString)
            cnt = 0
            for j in children:
                subgeom = self._build_geometry(j)
                if subgeom is not None:
                    cnt += 1
                    geom.AddGeometry(subgeom)
            if cnt == 0:  # No geometries added
                return None
        elif gtype == "Polygon":
            geom = ogr.Geometry(ogr.wkbPolygon)
            for (i, j) in enumerate(children):
                subgeom = self._build_geometry(j)
                if subgeom is not None:
                    geom.AddGeometry(subgeom)
                elif i == 0:  # If exterior is invalid, return nothing
                    return None
        elif gtype == "LinearRing":
            geom = ogr.Geometry(ogr.wkbLinearRing)

            # get all chains in the correct order
            points_data_list = self._build_retrieve_chain_points(geom_idx)

            # merge chains
            pointsdata_ring = self._merge_pointsdata_list(points_data_list)
            if pointsdata_ring is None:
                return None

            cnt = 0
            p_first = None
            p_last = None
            for p in self._build_pointsdata_filter_removed(pointsdata_ring):
                if p_first is None:
                    p_first = p
                cnt += 1
                geom.AddPoint_2D(*(p[P_COORD]))
                p_last = p
            if p_last != p_first:
                geom.AddPoint_2D(*(p_first[P_COORD]))
                cnt += 1

            if cnt <= 3:  # LinearRing must contain 3 or more distinct points!
                if self.constraint_prevent_shape_removal:
                    print "Warning: LinearRing(%s) with %s points found!" % (geom_idx, cnt)
                    print filter(lambda p: p[P_REMOVED] is False, pointsdata_ring)
                    raise NotImplementedError("Error! Prevent shape removal didn't work properly")
                return None
        elif gtype == "LineString":
            geom = ogr.Geometry(ogr.wkbLineString)

            points_data_list = self._build_retrieve_chain_points(geom_idx)

            # merge chains
            pointsdata = self._merge_pointsdata_list(points_data_list)
            if pointsdata is None:
                return None

            cnt = 0
            for p in self._build_pointsdata_filter_removed(pointsdata):
                geom.AddPoint_2D(*(p[P_COORD]))
                cnt += 1

            if cnt < 2:
                # LineString must contain 2 or more distinct points!
                if self.constraint_prevent_shape_removal:
                    print "Warning: LineString(%s) with %s points found!" % (geom_idx, cnt)
                    print filter(lambda p: p[P_REMOVED] is False, pointsdata)
                    raise NotImplementedError("Error! Prevent shape removal didn't work properly")
                return None
        else:
            raise Exception("Build geometry type %s not implemented" % gtype)
        return geom

    def _build_pointsdata_filter_removed(self, pointsdata):
        for p in pointsdata:  # add points to the linearring (only those which are not removed)
            if p[P_REMOVED] is False:
                yield p

    def _merge_pointsdata_list(self, pointsdata_list):
        """ Merge a list of list of points (Make sure last and first point of every chain wont appear twice)
        """
        if len(pointsdata_list) == 0:
            return None
        result = copy.copy(pointsdata_list[0])
        i = 1
        while i < len(pointsdata_list):
            point_list = pointsdata_list[i]
            # by definition: multiple chains always share their endpoints
            result += point_list[1:]
            i += 1
        return result

    def _build_retrieve_chain_points(self, geom_idx):
        """ Get all chain points in the correct point order for the geometry
        :return: list of list points
        """
        (gtype, parent, children) = self.geometries[geom_idx]
        if gtype not in {"LinearRing", "LineString"}:
            raise ValueError("Can't retrieve chain points for geometry type={}".format(gtype))

        points_data_list = []
        # Geometry is made of 1 or more chains
        for c in children:
            chain = self.chains[c]
            points = chain[self.CHAIN_POINTS]

            # Direction?
            # A chain can be shared between 1 or 2 distinct geometries.
            # By definition, the order of points is reversed for the second parent.
            # (TODO: implement sharing chain on overlapping polygons -> chain could be shared between more than 2 geoms)
            if chain[self.CHAIN_PARENTS][0] == geom_idx:
                direction = DIRECTION_NORMAL
            elif chain[self.CHAIN_PARENTS][1] == geom_idx:
                direction = DIRECTION_REVERSE
            else:
                # Parent points to chain c as a children. But geom_idx is not in chain c parents. Impossible
                print "chain error: geomidx=%s, chain=%s" % (geom_idx, c)
                raise Exception("Inconsistency: Parent's children is not in children parents".format(gtype))

            if direction == DIRECTION_REVERSE:
                points = points[::-1]
            points_data_list.append(points)
        return points_data_list

    def to_wkb(self, key):
        """ Get the wkb (binary string) for a given key
        :param key: geometry identifier
        :return: wkb (binary string)
        """
        # generate wkb for all geometries
        i = self.keys[key]
        geom = self._build_geometry(i)
        if geom is None:
            return None
        return geom.ExportToWkb(1)

#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from collections import defaultdict
import itertools
from simplipy import geotool
from simplipy.util import P_COORD, DIRECTION_NORMAL, DIRECTION_REVERSE, CChain, CGeometry, is_closed_chain
from simplipy.tools import average_segment_length_sample, list_difference


def point_key(p, k):
    # point_key: use this to snap points that are almost identical
    return int(p[P_COORD][0] / k) * k, int(p[P_COORD][1] / k) * k


def coord_key(coord, k):
    return int(coord[0] / k) * k, int(coord[1] / k) * k


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
        return key in self.junctions

    def get(self, key):
        return self.junctions.get(key)


def snap_coordinates(chaindb, snap_distance):
    """ Fix topology errors by snapping together points with nearly identical coordinates """
    snap_qdistance = snap_distance**2
    get_grid_id = lambda (x, y): (int(x / snap_distance), int(y / snap_distance))
    grid = defaultdict(list)  # grid[grid_id] = list of (chain_id, point_idx)

    # Map points into a grid with areas width=snap_distance. Two points in the same grid area or neighbor grid area
    # are candidates of distance(point1, point2) <= snap_distance
    for (chain_id1, chain) in enumerate(chaindb.chains):
        for p_idx1, point in enumerate(chain.points):
            grid_id = get_grid_id(point[P_COORD])
            grid[grid_id].append((chain_id1, p_idx1))

    # Compare all pair of points between areas and neighbor areas
    # Given an area X, its neighbor areas are: A B C D F G H and I, as shown in the following diagram:
    # -------
    # |A|B|C|
    # |D|X|F|
    # |G|H|I|
    # -------
    # Since we will iterate over all areas X, to avoid double/triple comparisons we will only compare points
    # from area X with points of areas X, F, G, H and I.
    # Note that, for example, points between areas A and X will be done when the center area is A (A=X' and E=I')
    chains = chaindb.chains
        gx, gy = grid_id
        # X-X points
        for (chain_id1, p_idx1), (chain_id2, p_idx2) in itertools.combinations(chains_points, 2):
            chain1 = chains[chain_id2].points
            if chain_id1 == chain_id2 and is_closed_chain(chain1) and sorted((p_idx1, p_idx2)) == (0, len(chain1)-1):
                # First and last point from closed chain are considered (and has to be) the same in a linearring.
                continue

            p1 = chain1[p_idx1][P_COORD]
            p2 = chains[chain_id2].points[p_idx2][P_COORD]
            if geotool.distance(p1[0], p1[1], p2[0], p2[1]) <= snap_distance:
                chains[chain_id2].points[p_idx2][P_COORD] = (p1[0], p1[1])

        # X-(F,G,H,I)
        for grid_id2 in ((gx + 1, gy),  # F
                         (gx - 1, gy + 1),  # G
                         (gx, gy + 1),  # H
                         (gx + 1, gy + 1),  # I
                         ):
            chains_points2 = grid.get(grid_id2)
            if not chains_points2:
                continue

            for (chain_id1, p_idx1), (chain_id2, p_idx2) in itertools.product(chains_points, chains_points2):
                p1 = chains[chain_id1].points[p_idx1][P_COORD]
                p2 = chains[chain_id2].points[p_idx2][P_COORD]
                if geotool.distance(p1[0], p1[1], p2[0], p2[1]) <= snap_distance:
                    chains[chain_id2].points[p_idx2][P_COORD] = (p1[0], p1[1])


def infer_topology(chaindb):
    """ Infers topology from geometries store in ChainDB and updates ChainDB geometries and chains so that
     chains shared by multiple geometries are the same chain object."""
    junction_points = JunctionPoints()

    debug = False
    if debug:
        chaindb.print_geoms()
        chaindb.print_chains()

    # Identify junctions between chains
    # http://bost.ocks.org/mike/topology/ (Step 2.Join)
    # TODO: Improve this, very close points can be not detect as such (dist<K) when they lay in distinct
    # parts of the point-to-grid map

    avg_segment_size = average_segment_length_sample(chaindb.chains, max_sample_size=100000)
    # snap_distance = chaindb.constraint_use_topology_snap_precision
    snap_distance = avg_segment_size * 0.0025  # Same constant used by mapshaper.org

    snap_coordinates(chaindb, snap_distance)

    # 1 - Map points
    point_map = {}  # may crash memory
    for (chain_id, chain) in enumerate(chaindb.chains):
        for point in chain.points:
            key = point_key(point, snap_distance)
            chain_idx_list = point_map.get(key)
            if chain_idx_list is None:
                point_map[key] = [chain_id]
            else:
                chain_idx_list.append(chain_id)

    # 2 - Detect junctions
    for (c, chain) in enumerate(chaindb.chains):
        last_key = point_key(chain.points[0], snap_distance)
        last_group = point_map.get(last_key)
        for p in chain.points[1:]:
            key = point_key(p, snap_distance)
            group = point_map.get(key)
            if group != last_group:
                join = list_difference(group, last_group)
                leaves = list_difference(last_group, group)
                if len(join) > 0:
                    junction_points.add_chain(key, c)
                if len(leaves) > 0:
                    junction_points.add_chain(last_key, c)
                last_group = group
            last_key = key

    # 3 - Split chains by junction
    junction_to_junction = {}

    def mark_junction_to_junction_chain(key1, key2, chain_idx):
        chain_idx_list = junction_to_junction.get((key1, key2))
        if chain_idx_list is None:
            junction_to_junction[(key1, key2)] = [chain_idx]
        else:
            chain_idx_list.append(chain_idx)

    def _get_j2j_chain(key1, key2, chain_points):
        chain_idxs_marked = junction_to_junction.get((key1, key2))
        if chain_idxs_marked is not None:
            for chain_idx2 in chain_idxs_marked:
                # verify that it's the same chain
                p1 = chain_points
                p2 = chaindb.chains[chain_idx2].points

                if point_key(p1[0], snap_distance) != point_key(p2[0], snap_distance) or point_key(p1[-1], snap_distance) != point_key(p2[-1], snap_distance):
                    raise Exception("this cant happen (j2j)")

                if point_key(p1[1], snap_distance) == point_key(p2[1], snap_distance):
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
    debug = False
    for geom in chaindb.geometries:
        if geom.type != "LinearRing":
            continue
        if debug:
            print "---------------------"
            print "Geom %s" % geom.parent
        geom_chains = geom.children

        new_chain_indexes = []
        chain_created = False
        for c in geom_chains:
            if debug:
                print "CHAIN %s (parent=%s)" % (c, chaindb.chains[c].parents)
                tab = "    "
            disable_chain = True
            chain = chaindb.chains[c]
            if len(chain.parents) != 1:
                raise Exception("expecting parents size = 1!?")
            points = chain.points
            start_key = point_key(points[0], snap_distance)

            i = 0
            j = 1
            while j < len(points):
                p = points[j]
                key = point_key(p, snap_distance)
                if debug and c == 1002:
                    print "CHAIN %s (parent=%s)" % (c, chaindb.chains[c].parents), i, j
                if junction_points.has_key(key):

                    subchain = points[i:j+1]
                    (direction, chain_idx2) = get_junction_to_junction_chain(start_key, key, subchain)

                    if debug:
                        print tab, "start_key=%s -> %s" % (start_key, key)
                        print tab, "Chain %s----->%s" % (list(junction_points.get(start_key)),
                                                         list(junction_points.get(key)))
                        print tab, "subchain[%s:%s]" % (i, j), direction, chain_idx2
                        if c == 1002:
                            print tab, "subchain points:", subchain

                    # check if junction to junction A->B->A
                    if chain_idx2 is not None:
                        if chaindb.chains[chain_idx2].parents == chaindb.chains[c].parents:
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
                            chain_idx2 = len(chaindb.chains)
                            chaindb.chains.append(CChain(parents=[chain.parents[0]], points=subchain))
                            dbg = "new"
                        mark_junction_to_junction_chain(start_key, key, chain_idx2)
                    else:
                        chain_created = True
                        # two chains from distinct polygons will share the memory space
                        # subchain = self.chains[chain_idx2].points
                        dbg = "reused %s" % chain_idx2
                        if debug:
                            print tab, "Reuse ", chain_idx2, "(parents=", chaindb.chains[chain_idx2].parents, ")"
                        if chain.parents[0] in chaindb.chains[chain_idx2].parents:
                            if debug:
                                print tab, "matched chain:", chaindb.chains[chain_idx2]
                            raise ValueError("Data inconsistency. chain_idx={} already has {} as parent"
                                             .format(chain_idx2, chain.parents[0]))

                        chaindb.chains[chain_idx2].parents.append(chain.parents[0])

                        # chain_idx2 = len(self.chains)
                        # self.chains.append(CChain(parents=chain.parents, points=subchain))
                        # Subchain already saved
                    new_chain_indexes.append(chain_idx2)
                    if debug:
                        print tab, "SPLIT %s to chainid=%s" % (c, chain_idx2), dbg
                        print tab, "new parents=", chaindb.chains[chain_idx2].parents
                    i = j
                    start_key = key
                j += 1
            if disable_chain:
                disable_chains.add(c)
        if debug:
            print "geom new chains=%s" % new_chain_indexes

        if len(new_chain_indexes) > 0:
            for parent_geom_idx in chain.parents:
                parent_cgeom = chaindb.geometries[parent_geom_idx]
                chaindb.geometries[parent_geom_idx] = CGeometry(type=parent_cgeom.type,
                                                                parent=parent_cgeom.parent,
                                                                children=new_chain_indexes)
                # geom.children = new_chain_indexes

        for c in disable_chains:
            chaindb.chains[c] = None

    # 4 - Share chains
    # print_chains()
    if debug:
        chaindb.print_geoms()
        chaindb.paint_chains()
    print "TOPOLOGY INFERED"
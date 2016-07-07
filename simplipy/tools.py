#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from collections import Counter
from simplipy.util import P_COORD
from simplipy import geotool


def shortest_path_dag_ordered(graph, start, end):
    # Pre:
    # graph G is unweighted DAG.
    # v1 < v2 for all edges e=(v1,v2) in G,
    # note that e=(end, vx) can't be in G
    costs = {end: 0}
    parent = {}

    vertices = graph.keys()  # 'end' vertex isn't here
    for v1 in sorted(vertices, reverse=True):
        for v2 in graph[v1]:
            cost = costs.get(v2)
            if cost is not None: # If there's a path to end
                costs[v1] = cost + 1
                parent[v1] = v2

    if costs.get(start) is not None:
        # there is a path to 'end'.
        path = []
        v = start
        while v != end:
            path.append(v)
            v = parent[v]
        path.append(end)
        return path
    return None


def list_difference(l1, l2):
    c1 = Counter(l1)
    c2 = Counter(l2)
    diff = c1 - c2
    return list(diff.elements())


def average_segment_length_sample(chains, max_sample_size):
    """ Returns the average segment length from a sample of all segments in self.chains (from original geometry!)
    :param chains: ChainDB.chains object
    """

    distances = []
    for (c, chain) in enumerate(chains):
        if chain is None:
            continue
        points = iter(chain.points)
        last = next(points)[P_COORD]
        for p in points:
            p = p[P_COORD]
            if last != p:
                dist = geotool.distance(p[0], p[1], last[0], last[1])
                distances.append(dist)
                if len(distances) > max_sample_size:
                    break
            last = p
        if len(distances) > max_sample_size:
            break
    if len(distances) == 0:
        raise ValueError("Could not find any segment to get average segment length")
    avg = sum(distances) / len(distances)
    return avg

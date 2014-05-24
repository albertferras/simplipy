__author__ = 'albert'


def shortest_path_dag_ordered(G, start, end):
    # Pre:
    # graph G is unweighted DAG.
    # v1 < v2 for all edges e=(v1,v2) in G,
    # note that e=(end, vx) can't be in G
    costs = {}
    costs[end] = 0
    parent = {}

    V = G.keys() # 'end' vertex isn't here
    for v1 in sorted(V, reverse=True):
        for v2 in G[v1]:
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

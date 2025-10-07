# Copyright (c) 2025 ETH Zurich.
#                    All rights reserved.
#
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# Main author: Alessandro Maissen

# validate a created Fat-Tree topology

from random import randint
from networkx import Graph, is_connected
from networkx.algorithms import bipartite
from networkx.classes.function import degree
from .common import has_double_edges, is_directed, listgraph_to_nxgraph


def validate(graph : [[int]], k : int) -> int:
    print("--> Validating FatTree(%d):" %k)

    # check sizes
    if len(graph) != 5*(k**2)/4:
        print("     --> construction error: incorrect number of nodes")
        return 0
    if sum([len(node) for node in graph]) != k*(k**2)/4 + k*k*(k/2) + k*(k/2)*(k/2): # core edges + aggregation edges + edge edges
        print("     --> construction error: incorrect number of edges")
        return 0
    
    # check for double edges
    if has_double_edges(graph):
        print("     --> construction error: has double edges")
        return 0

    # check if graph is undirected
    if is_directed(graph):
        print("     --> construction error: not undirected")
        return 0

    # construct a NetworkX graph (undirected, no multi-edges) for further validation
    nx_graph = listgraph_to_nxgraph(graph)

    # check if graph is connected
    if not is_connected(nx_graph):
        print("     --> construnction error: not conncected")
        return 0
    
    # check if graph is bipartite
    if not bipartite.is_bipartite(nx_graph):
         print("     --> construnction error: not bipartid")
         return 0

    # check sizes of two bipartite sets
    nodesA, nodesB = bipartite.sets(nx_graph)
    len_nA = len(nodesA)
    len_nB = len(nodesB)
    if not(len_nA == k*k/2 and len_nB == k*k/2 + k**2/4) and not (len_nB == k*k/2 and len_nA == k*k/2 + k**2/4):
        print("     --> construnction error: incorrect sizes of bipartite sets")
        return 0
    
    # exploit the bipartite sets
    aggregation = set()
    edge_core = set()
    if len_nA == k*k/2:
        aggregation = list(nodesA)
        edge_core = list(nodesB)
    else:
        edge_core = list(nodesA)
        aggregation = list(nodesB)
    
    # check degrees of edge and aggregation
    degrees_aggregation = degree(nx_graph, aggregation)
    degrees_edge_core = degree(nx_graph, edge_core)

    if len(set([d[1] for d in degrees_aggregation])) != 1 or len(set([d[1] for d in degrees_edge_core])) != 2:
        print("     --> construnction error: degree are not all the same in one layer")
        return 0

    return 1

def generate_random_parameters(kmax : int, number : int) -> [int]:
    parameters = []
    while len(parameters) != number:
        k = randint(2, kmax)
        if(k % 2 == 0):
            parameters.append(k)
    
    return parameters

def validate_fattree():
    from .FatTreeGenerator import FatTreeGenerator

    fts = generate_random_parameters(32, 5)

    results = []
    for ft in fts:
        g = FatTreeGenerator().make(ft)
        results.append(validate(g, ft))
    
    if sum(results) == len(fts):
        print("VALIDATION PASSED")
    else:
        print("VALIDATION NOT PASSED")

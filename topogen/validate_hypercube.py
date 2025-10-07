# Copyright (c) 2025 ETH Zurich.
#                    All rights reserved.
#
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# Main author: Alessandro Maissen

# validate a created HyperCube

from .common import has_double_edges, is_directed, listgraph_to_nxgraph
from networkx import Graph, is_connected
from networkx.classes.function import degree
from random import randint


def validate(graph : [[int]], n : int):
    print("--> Validating %dD-HyperCube:" %n)
    passed = 1

    # check sizes
    if len(graph) != 2**n:
        print("     --> construction error: incorrect number of nodes")
        passed = 0
    if sum([len(node) for node in graph]) != n * 2**n:
        print("     --> construction error: incorrect number of edges")
        passed = 0
    
    # check for double edges
    if has_double_edges(graph):
        print("     --> construction error: has double edges")
        passed = 0

    # check if graph is undirected
    if is_directed(graph):
        print("     --> construction error: not undirected")
        passed = 0

    # construct a NetworkX graph (undirected, no multi-edges) for further validation
    nx_graph = listgraph_to_nxgraph(graph)

    # check if graph is connected
    if not is_connected(nx_graph):
        print("     --> construnction error: not conncected")
        passed = 0

    # check degree of each node is equal to n (dimension of hypercube)
    degrees = degree(nx_graph)
    for d in degrees:
        if d[1] != n:
            print("     --> construnction error: degree not equal to n")
            passed = 0
            break

    return passed

def generate_random_parameters(nmax : int, number : int):
    parameters = []
    for _ in range(number):
        n = randint(1, nmax)
        parameters.append(n)
    
    return parameters

def validate_hypercube():
    from .HypercubeGenerator import HypercubeGenerator

    hypercubes = generate_random_parameters(10, 5)

    results = []
    for h in hypercubes:
        g = HypercubeGenerator().make(h)
        results.append(validate(g, h))
    
    if sum(results) == len(hypercubes):
        print("VALIDATION PASSED")
    else:
        print("VALIDATION NOT PASSED")

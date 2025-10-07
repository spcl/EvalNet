# Copyright (c) 2025 ETH Zurich.
#                    All rights reserved.
#
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# Main author: Jascha Krattenmacher

# validate a created express Mesh

from .common import has_double_edges, is_directed, listgraph_to_nxgraph
from networkx import Graph, is_connected
from networkx.classes.function import degree
from random import randint
from .expressMeshGenerator import expressMeshGenerator


def validate(graph : [[int]], n1 : int, n2 : int, g : int):
    print("--> Validating %dx%d-%dexpMesh:" %(n1,n2,g))
    passed = 1

    # check sizes
    if len(graph) != n1*n2:
        print("     --> construction error: incorrect number of nodes")
        passed = 0
    
    # check for double edges
    if has_double_edges(graph):
        print("     --> construction error: has double edges")
        passed = 0

    # check if graph is undirected
    if is_directed(graph):
        print("     --> construction error: not undirected")
        passed = 0

    # construct a Network graph (undirected, no multi-edges) for further validation
    nx_graph = listgraph_to_nxgraph(graph)

    # check if graph is connected
    if not is_connected(nx_graph):
        print("     --> construnction error: not conncected")
        passed = 0

    return passed

def generate_random_parameters(nmax : int, gmax : int, number : int):
    parameters = []
    for _ in range(number):
        n1 = randint(1, nmax)
        n2 = randint(1,nmax)
        g = randint(2,gmax)
        parameters.append((n1,n2,g))
    
    return parameters

def validate_expMesh():
    meshes = generate_random_parameters(6,4, 5)

    results = []
    for m in meshes:
        g = ExpressMeshGenerator().make(m)
        results.append(validate(g, m))
    
    if sum(results) == len(meshes):
        print("VALIDATION PASSED")
    else:
        print("VALIDATION NOT PASSED")

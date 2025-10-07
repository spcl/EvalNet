# Copyright (c) 2025 ETH Zurich.
#                    All rights reserved.
#
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# Main author: Alessandro Maissen

# validate a created Delorme topology

import networkx as nx


def validate(graph : [[int]], q : int):
    print("--> Validating Delorme(%d):" %q)
    # check sizes
    if len(graph) != (q+1)*(q**2+1):
        print("     --> construction error: incorrect number of nodes")
        return 0

    # construct a NetworkX graph (undirected, no multi-edges) for further validation
    nx_graph = nx.Graph()
    for i in range(len(graph)):
        nx_graph.add_node(i)
        for j in graph[i]:
            nx_graph.add_edge(i, j)

    # check if graph is connected
    if not nx.is_connected(nx_graph):
        print("     --> construnction error: not conncected")
        return 0

    # check max degree
    max_degree = max(dict(nx_graph.degree).values())
    if max_degree != q+1:
         print("     --> construction error: incorrect degrees")
         return 0

    # check diameter
    diameter = nx.diameter(nx_graph)
    if diameter != 3:
        print("     --> construction error: incorrect diameter")
        return 0

    return 1

def validate_delorme():
    from .DelormeGenerator import DelormeGenerator

    g = DelormeGenerator().make(8)
    
    if validate(g, 8):
        print("VALIDATION PASSED")
    else:
        print("VALIDATION NOT PASSED")

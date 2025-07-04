# Copyright (c) 2025 ETH Zurich.
#                    All rights reserved.
#
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# Main author: Jascha Krattenmacher

import networkx as nx
import random 
from math import factorial


def validate(graph : [[int]], n : int, k : int):
    print("--> Validating arrangement Network(%d,%d):" %(n,k))
    # check sizes
    if len(graph) != factorial(n)/factorial(n-k):
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
        print("     --> construction error: not conncected")
        return 0

    return 1

def generate_random_parameters(nmax: int, num_tests: int) -> [int]:
    params = []
    for i in range(num_tests):
        n = random.randint(3, nmax)
        k = random.randint(2,n-1)
        
        params.append((n,k))
    return params

def validate_arrangementNetwork():
    from .ArrangementNetworkGenerator import ArrangementNetworkGenerator

    params = generate_random_parameters(10, 5)
    results = []
    
    for param in params:
        g = ArrangementNetworkGenerator().make(param[0],param[1])
        results.append(validate(g, param[0], param[1]))
    
    if sum(results)==len(params):
        print("VALIDATION PASSED")
    else:
        print("VALIDATION NOT PASSED")

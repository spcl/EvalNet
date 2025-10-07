# Copyright (c) 2025 ETH Zurich.
#                    All rights reserved.
#
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# Main author: Jascha Krattenmacher

# use algorithm of Jens Domke
# (n,k) ArrangementNetwork

# PARAMETERS
# n: maximum integer n to chose from the (n,k) arrangement araph -> n > 0
# k: number of elements k in the permutation of the (n,k) arrangement graph -> k > 0 and k <= n

# VARIABLES 
# N: number of routers/nodes in total

# PRECONDITIONS
# k > 0, n > k

from .TopologyGenerator import TopologyGenerator
from .validate_arrangementNetwork import validate
from functools import reduce
from math import ceil, factorial
from itertools import permutations


class ArrangementNetworkGenerator(TopologyGenerator):
    def __init(self):
        super(ArrangementNetworkGenerator,self).__init__()
    
    def make(self, n : int, k : int) -> [[int]]:
        assert(n > 0 and (k > 0 and k < n))
         
        topology = {}

        # generate all switches
        j = 0
        for idx_tuple in permutations(range(1, n + 1), k):
            idx_vector = list(idx_tuple)
            topology[str(idx_vector)] = [j,[]]
            j += 1

        # connect all switches (multiple times if possible)
        min_ports_needed_for_round = k * (n - k)
        for idx_tuple in permutations(range(1, n + 1), k):
            idx_vector_1 = list(idx_tuple)
            switch1 = topology[str(idx_vector_1)]
    
            for i in range(k):
                p_i = idx_vector_1[i]
                idx_vector_2 = idx_vector_1[:]
                # only consider q_i > p_i, or we'd get two links per edge
                # obviously q_i MUST be valid w.r.t to arrangement graph def
                for q_i in [q_i for q_i in range(p_i + 1, n + 1) if idx_vector_1.count(q_i) == 0]:
                    idx_vector_2[i] = q_i
                    switch2 = topology[str(idx_vector_2)]
                    switch1[1].append(switch2[0]) #append id2 to adj list of id1
                    switch2[1].append(switch1[0])
    

        arrNetworkTopology = [ entry[1]  for entry in topology.values() ] 

        return arrNetworkTopology
    
    def validate(self, topo : [[int]], n : int, k: int) -> bool:
        return validate(topo,n,k)
    
    def get_folder_path(self):
        return super(ArrangementNetworkGenerator,self).get_folder_path() + "arrangementNetworks/"

    def get_file_name(self, n : int, k : int) -> str:
        return str(n) + "arrNetwork." + str(k) + ".adj.txt"

############# Helper Functions ##############

def _get_switch_name(prefix, z):
    return '%s<%s>' % (prefix, ','.join([str(x) for x in z]))

def _binomial(n, k):
    if k < 0 or k > n:
        return 0
    elif k == 0 or n == k:
        return 1
    elif k == 1:
        return n
    v = [z for z in range(n + 1)]
    return int(reduce(lambda x, y: x * y,
                      v[n - k + 1:]) / reduce(lambda x, y: x * y, v[1:k + 1]))

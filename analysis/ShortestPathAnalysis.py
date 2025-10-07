# Copyright (c) 2025 ETH Zurich.
#                    All rights reserved.
#
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# Main author: Jascha Krattenmacher

from .Analysis import Analysis
from .results import Results
from .common import is_in_db
from .simplepmap import pmap
from topogen.common import from_list_graph_to_matrix_graph, from_list_graph_to_sparse_matrix
from itertools import permutations
import numpy as np
import scipy.sparse as ss
import random


class ShortestPathAnalysis(Analysis):
    edgetype = edgetype = np.uint32

    def __init__(self, datafilename="shortest_paths.db", number_of_samples=1000000, all_combinations=False):
        super(ShortestPathAnalysis,self).__init__()
        self.datafile = self.datafilefolder + datafilename
        self.number_of_samples = number_of_samples
        self.all_combinations = all_combinations

    def analyse(self, networks, maxlength : int, sparse=False, parallel=False):
        res = Results(self.datafile)

        for network in networks:          

            print("Analysing shortest paths on %s with %d endnodes" %(network.name,network.N))
            if not is_in_db(network,res,maxlength):
                
                if sparse: 
                    sparse_matrix_graph = from_list_graph_to_sparse_matrix(network.get_topo())
                    sparse_matrix_graph.edge = network.edge
                    sparse_matrix_graph.vertices = network.R
                    collect = res.collector(file="shortest_paths.py", tag="shortest-path", maxlen = maxlength, len=Results.Int, multiplicity=Results.Int, topo=network.name, n_r=network.R, r=network.nr, n_e=network.N, p=network.p) 
                    self.__count_shortest_paths_sparse(graph=sparse_matrix_graph, limit=maxlength, collect=collect, count=self.number_of_samples, parallel=parallel)
                    res.commit()
                else:
                    matrix_graph = from_list_graph_to_matrix_graph(network.get_topo())
                    matrix_graph.edge = network.edge
                    matrix_graph.vertices = network.R
                    collect = res.collector(file="shortest_paths.py", tag="shortest-path", maxlen = maxlength, len=Results.Int, multiplicity=Results.Int, topo=network.name, n_r=network.R, r=network.nr, n_e=network.N, p=network.p) 
                    self.__count_shortest_paths(graph=matrix_graph, limit=maxlength, collect=collect, count=self.number_of_samples)
                    res.commit()

            else:
                print("     --> skip, already in database")

        res.close()
    
    # private methods
    def __count_shortest_paths_sparse(self, graph, limit, collect, count=100000, parallel=False):
        r = list(range(0, graph.edge))
        if self.all_combinations:
            pairs = list(permutations(r, 2))
        else:
            pairs = [random.sample(r, 2) for _ in range(0, count)]
        
        acc = ss.identity(graph.vertices, dtype=self.edgetype, format='csr')
        is_shortest = np.ones(count, dtype=np.bool)

        for i in range(1, limit+1):
            
            if parallel:
                step = self.__pmult(acc,graph)
            else:
                step = acc.dot(graph)
                
            for index, pair in enumerate(pairs):
                s = pair[0]
                t = pair[1]
                if is_shortest[index] and step[s,t]:
                    collect(len=i, multiplicity=step[s,t])
                    is_shortest[index] = False

            acc = step

    def __count_shortest_paths(self, graph, limit, collect, count = 100000):
        r = list(range(0, graph.edge))
        if self.all_combinations:
            pairs = list(permutations(r, 2))
        else:
            pairs = [random.sample(r, 2) for _ in range(0, count)]
        
        acc = np.identity(graph.vertices, dtype=self.edgetype)
        connected = np.zeros_like(graph, dtype=np.bool_)

        for i in range(1, limit+1):
            step = acc.dot(graph)
                
            shortest = np.multiply(step, ~connected) # elem-wise mask
            connected += (step != 0)
            
            for s,t in pairs:
                if shortest[s,t]:
                    collect(len=i, multiplicity=step[s,t])

            acc = step
    
    def __pmult(self, A, B):
        A = A.asformat("csr")
        BS = 1000 
        nblocks = int(A.shape[0] / BS)
        aa = [A[i*BS:(i+1)*BS, :] for i in range(0, nblocks)]
        if nblocks*BS < A.shape[0]:
            aa.append(A[nblocks*BS:, :])
        qs = pmap(lambda a: a*B, aa)
        return ss.vstack(qs)

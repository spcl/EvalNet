# Copyright (c) 2025 ETH Zurich.
#                    All rights reserved.
#
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# Main author: Haoran Zhao
#
# Contributions: Kartik Lakhotia

# Implemented based on Paper: Grands Graphes de Degre et Diametre Donnes

# PARAMETERS
# q: size of Galois field (q:= 2^(2*a-1), where a = 1,2,3,... and q an odd power of 2)

# VARIABLES
# sigma: 2^a, where q = 2^(2*a-1)

# PRECONDITIONS
# q:= 2^(2*a-1), an odd power of 2

# ADDITIONAL NOTES:
# currently only support q = 8

from .TopologyGenerator import TopologyGenerator
from .validate_delorme import validate

import numpy as np


class DelormeGenerator(TopologyGenerator):
    def __init(self):
        super(DelormeGenerator,self).__init__()

    def vector_mul(self, point, a):
        out = np.zeros(4,dtype=int)
        for i in range(4):
            out[i] = self.gf.mul[a][point[i]]
        return out

    def gen_v(self, v):
        vs = []
        for i in range(2,self.q):
            v_tmp =  self.vector_mul(v,i)
            vs.append(tuple(v_tmp))
        return vs

    def get_polarity(self, points):
        u0 = points[0]
        u1 = points[1]
        u2 = points[2]
        u3 = points[3]  
        a = self.gf.add[self.gf.mul[u0][u1]][self.gf.mul[u2][u3]]
        p01 = a
        p23 = a
        p02 = u0
        p31 = u1
        p03 = u2
        p12 = u3
        for i in range(self.sigma//2-1):
            p01 = self.gf.mul[a][p01]
            p23 = self.gf.mul[a][p23]

        for i in range(self.sigma-1):
            p02 = self.gf.mul[u0][p02]
            p31 = self.gf.mul[u1][p31]
            p03 = self.gf.mul[u2][p03]
            p12 = self.gf.mul[u3][p12]
        
        matrix = np.array([[0,p23,p31,p12],[p23,0,p03,p02],[p31,p03,0,p01],[p12,p02,p01,0]])
        return matrix

    def point_on_line(self, matrix, point):
        res = np.zeros(4,dtype=int)
        for i in range(4):
            c0 = self.gf.mul[matrix[i][0]][point[0]]
            c1 = self.gf.mul[matrix[i][1]][point[1]]
            c2 = self.gf.mul[matrix[i][2]][point[2]]
            c3 = self.gf.mul[matrix[i][3]][point[3]]
            res[i] = self.gf.add[c0][self.gf.add[c1][self.gf.add[c2][c3]]]
        return np.sum(res) == 0

    def make(self, q : int):
        alpha = int((np.log2(q) + 1)/2)
        self.sigma = 2**alpha
        self.q = q 
        V = (1+q)*(1+q**2)
        self.gf = GF(q)

        vectors = []
        vectors_1 = []
        node_map = {}
        graph = [[] for _ in range(V)]

        # get all 1-d subspace vector of GF(3,q)
        for d1 in range(q):
            for d2 in range(q):
                for d3 in range(q):
                    for d4 in range(q):
                        v = (d1,d2,d3,d4)
                        vectors.append(v)
                        vectors_1.append(v)
        vectors.remove((0,0,0,0))
        vectors_1.remove((0,0,0,0))
        # get unique 1-d subspace vector of GF(3,q) (one basis vector for one subspace)
        for idx,vec in enumerate(vectors_1):
            if vec in vectors:
                for sv in self.gen_v(vec):
                    if sv in vectors:
                        vectors.remove(sv)

        for idx,v in enumerate(vectors):
            node_map[v] = idx
        # add connection between 1-d subspace vectors
        for idx,v in enumerate(vectors):
            m =self.get_polarity(v)
            source = idx
            for vv in vectors:
                if self.point_on_line(m,vv):
                    dest = node_map[vv]
                    if dest != source:
                        graph[source].append(dest)

        # reorder vertices for a more human readable format (consecutive vertex IDs in a group/star)
        vertex_reorder = {}
        idx = 0
        for src in range(len(graph)):
            if (len(graph[src]) == q):
                assert (src not in vertex_reorder)
                vertex_reorder[src] = idx
                idx += 1
                for dst in graph[src]:
                    assert (dst not in vertex_reorder)
                    vertex_reorder[dst] = idx
                    idx += 1 

        graph_reordered = [[] for _ in range(V)]
        for src in range(len(graph)): 
            assert (src in vertex_reorder)
            src_reordered = vertex_reorder[src]
            for dst in graph[src]:
                assert (dst in vertex_reorder)
                dst_reordered = vertex_reorder[dst]
                graph_reordered[src_reordered].append(dst_reordered)            
            graph_reordered[src_reordered].sort()

        return graph_reordered

    def validate(self, topo : [[int]], q : int) -> bool:
        return validate(topo,q)
    
    def get_folder_path(self):
        return super(DelormeGenerator,self).get_folder_path() + "Delormes/"

    def get_file_name(self, q : int) -> str:
        return "Delorme." + str(q) + ".adj.txt"

class GF:
    def __init__(self,q):
        if q == 2:
            self.add = [[0,1],
                        [1,0]]
            self.mul = [[0,0],
                        [0,1]]    
        if q == 8:
            self.add = [[0, 1, 2, 3, 4, 5, 6, 7],
                        [1, 0, 3, 2, 5, 4, 7, 6],
                        [2, 3, 0, 1, 6, 7, 4, 5],
                        [3, 2, 1, 0, 7, 6, 5, 4],
                        [4, 5, 6, 7, 0, 1, 2, 3],
                        [5, 4, 7, 6, 1, 0, 3, 2],
                        [6, 7, 4, 5, 2, 3, 0, 1],
                        [7, 6, 5, 4, 3, 2, 1, 0]]
            self.mul = [[0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 1, 2, 3, 4, 5, 6, 7],
                        [0, 2, 4, 6, 5, 7, 1, 3],
                        [0, 3, 6, 5, 1, 2, 7, 4],
                        [0, 4, 5, 1, 7, 3, 2, 6],
                        [0, 5, 7, 2, 3, 6, 4, 1],
                        [0, 6, 1, 7, 2, 4, 3, 5],
                        [0, 7, 3, 4, 6, 1, 5, 2]]
        if q == 32:
            self.add=[
                [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31],
                [1,0,3,2,5,4,7,6,9,8,11,10,13,12,15,14,17,16,19,18,21,20,23,22,25,24,27,26,29,28,31,30],
                [2,3,0,1,6,7,4,5,10,11,8,9,14,15,12,13,18,19,16,17,22,23,20,21,26,27,24,25,30,31,28,29],
                [3,2,1,0,7,6,5,4,11,10,9,8,15,14,13,12,19,18,17,16,23,22,21,20,27,26,25,24,31,30,29,28],
                [4,5,6,7,0,1,2,3,12,13,14,15,8,9,10,11,20,21,22,23,16,17,18,19,28,29,30,31,24,25,26,27],
                [5,4,7,6,1,0,3,2,13,12,15,14,9,8,11,10,21,20,23,22,17,16,19,18,29,28,31,30,25,24,27,26],
                [6,7,4,5,2,3,0,1,14,15,12,13,10,11,8,9,22,23,20,21,18,19,16,17,30,31,28,29,26,27,24,25],
                [7,6,5,4,3,2,1,0,15,14,13,12,11,10,9,8,23,22,21,20,19,18,17,16,31,30,29,28,27,26,25,24],
                [8,9,10,11,12,13,14,15,0,1,2,3,4,5,6,7,24,25,26,27,28,29,30,31,16,17,18,19,20,21,22,23],
                [9,8,11,10,13,12,15,14,1,0,3,2,5,4,7,6,25,24,27,26,29,28,31,30,17,16,19,18,21,20,23,22],
                [10,11,8,9,14,15,12,13,2,3,0,1,6,7,4,5,26,27,24,25,30,31,28,29,18,19,16,17,22,23,20,21],
                [11,10,9,8,15,14,13,12,3,2,1,0,7,6,5,4,27,26,25,24,31,30,29,28,19,18,17,16,23,22,21,20],
                [12,13,14,15,8,9,10,11,4,5,6,7,0,1,2,3,28,29,30,31,24,25,26,27,20,21,22,23,16,17,18,19],
                [13,12,15,14,9,8,11,10,5,4,7,6,1,0,3,2,29,28,31,30,25,24,27,26,21,20,23,22,17,16,19,18],
                [14,15,12,13,10,11,8,9,6,7,4,5,2,3,0,1,30,31,28,29,26,27,24,25,22,23,20,21,18,19,16,17],
                [15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0,31,30,29,28,27,26,25,24,23,22,21,20,19,18,17,16],
                [16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15],
                [17,16,19,18,21,20,23,22,25,24,27,26,29,28,31,30,1,0,3,2,5,4,7,6,9,8,11,10,13,12,15,14],
                [18,19,16,17,22,23,20,21,26,27,24,25,30,31,28,29,2,3,0,1,6,7,4,5,10,11,8,9,14,15,12,13],
                [19,18,17,16,23,22,21,20,27,26,25,24,31,30,29,28,3,2,1,0,7,6,5,4,11,10,9,8,15,14,13,12],
                [20,21,22,23,16,17,18,19,28,29,30,31,24,25,26,27,4,5,6,7,0,1,2,3,12,13,14,15,8,9,10,11],
                [21,20,23,22,17,16,19,18,29,28,31,30,25,24,27,26,5,4,7,6,1,0,3,2,13,12,15,14,9,8,11,10],
                [22,23,20,21,18,19,16,17,30,31,28,29,26,27,24,25,6,7,4,5,2,3,0,1,14,15,12,13,10,11,8,9],
                [23,22,21,20,19,18,17,16,31,30,29,28,27,26,25,24,7,6,5,4,3,2,1,0,15,14,13,12,11,10,9,8],
                [24,25,26,27,28,29,30,31,16,17,18,19,20,21,22,23,8,9,10,11,12,13,14,15,0,1,2,3,4,5,6,7],
                [25,24,27,26,29,28,31,30,17,16,19,18,21,20,23,22,9,8,11,10,13,12,15,14,1,0,3,2,5,4,7,6],
                [26,27,24,25,30,31,28,29,18,19,16,17,22,23,20,21,10,11,8,9,14,15,12,13,2,3,0,1,6,7,4,5],
                [27,26,25,24,31,30,29,28,19,18,17,16,23,22,21,20,11,10,9,8,15,14,13,12,3,2,1,0,7,6,5,4],
                [28,29,30,31,24,25,26,27,20,21,22,23,16,17,18,19,12,13,14,15,8,9,10,11,4,5,6,7,0,1,2,3],
                [29,28,31,30,25,24,27,26,21,20,23,22,17,16,19,18,13,12,15,14,9,8,11,10,5,4,7,6,1,0,3,2],
                [30,31,28,29,26,27,24,25,22,23,20,21,18,19,16,17,14,15,12,13,10,11,8,9,6,7,4,5,2,3,0,1],
                [31,30,29,28,27,26,25,24,23,22,21,20,19,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0]
                ]
            self.mul=[
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31],
                [0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,5,7,1,3,13,15,9,11,21,23,17,19,29,31,25,27],
                [0,3,6,5,12,15,10,9,24,27,30,29,20,23,18,17,21,22,19,16,25,26,31,28,13,14,11,8,1,2,7,4],
                [0,4,8,12,16,20,24,28,5,1,13,9,21,17,29,25,10,14,2,6,26,30,18,22,15,11,7,3,31,27,23,19],
                [0,5,10,15,20,17,30,27,13,8,7,2,25,28,19,22,26,31,16,21,14,11,4,1,23,18,29,24,3,6,9,12],
                [0,6,12,10,24,30,20,18,21,19,25,31,13,11,1,7,15,9,3,5,23,17,27,29,26,28,22,16,2,4,14,8],
                [0,7,14,9,28,27,18,21,29,26,19,20,1,6,15,8,31,24,17,22,3,4,13,10,2,5,12,11,30,25,16,23],
                [0,8,16,24,5,13,21,29,10,2,26,18,15,7,31,23,20,28,4,12,17,25,1,9,30,22,14,6,27,19,11,3],
                [0,9,18,27,1,8,19,26,2,11,16,25,3,10,17,24,4,13,22,31,5,12,23,30,6,15,20,29,7,14,21,28],
                [0,10,20,30,13,7,25,19,26,16,14,4,23,29,3,9,17,27,5,15,28,22,8,2,11,1,31,21,6,12,18,24],
                [0,11,22,29,9,2,31,20,18,25,4,15,27,16,13,6,1,10,23,28,8,3,30,21,19,24,5,14,26,17,12,7],
                [0,12,24,20,21,25,13,1,15,3,23,27,26,22,2,14,30,18,6,10,11,7,19,31,17,29,9,5,4,8,28,16],
                [0,13,26,23,17,28,11,6,7,10,29,16,22,27,12,1,14,3,20,25,31,18,5,8,9,4,19,30,24,21,2,15],
                [0,14,28,18,29,19,1,15,31,17,3,13,2,12,30,16,27,21,7,9,6,8,26,20,4,10,24,22,25,23,5,11],
                [0,15,30,17,25,22,7,8,23,24,9,6,14,1,16,31,11,4,21,26,18,29,12,3,28,19,2,13,5,10,27,20],
                [0,16,5,21,10,26,15,31,20,4,17,1,30,14,27,11,13,29,8,24,7,23,2,18,25,9,28,12,19,3,22,6],
                [0,17,7,22,14,31,9,24,28,13,27,10,18,3,21,4,29,12,26,11,19,2,20,5,1,16,6,23,15,30,8,25],
                [0,18,1,19,2,16,3,17,4,22,5,23,6,20,7,21,8,26,9,27,10,24,11,25,12,30,13,31,14,28,15,29],
                [0,19,3,16,6,21,5,22,12,31,15,28,10,25,9,26,24,11,27,8,30,13,29,14,20,7,23,4,18,1,17,2],
                [0,20,13,25,26,14,23,3,17,5,28,8,11,31,6,18,7,19,10,30,29,9,16,4,22,2,27,15,12,24,1,21],
                [0,21,15,26,30,11,17,4,25,12,22,3,7,18,8,29,23,2,24,13,9,28,6,19,14,27,1,20,16,5,31,10],
                [0,22,9,31,18,4,27,13,1,23,8,30,19,5,26,12,2,20,11,29,16,6,25,15,3,21,10,28,17,7,24,14],
                [0,23,11,28,22,1,29,10,9,30,2,21,31,8,20,3,18,5,25,14,4,19,15,24,27,12,16,7,13,26,6,17],
                [0,24,21,13,15,23,26,2,30,6,11,19,17,9,4,28,25,1,12,20,22,14,3,27,7,31,18,10,8,16,29,5],
                [0,25,23,14,11,18,28,5,22,15,1,24,29,4,10,19,9,16,30,7,2,27,21,12,31,6,8,17,20,13,3,26],
                [0,26,17,11,7,29,22,12,14,20,31,5,9,19,24,2,28,6,13,23,27,1,10,16,18,8,3,25,21,15,4,30],
                [0,27,19,8,3,24,16,11,6,29,21,14,5,30,22,13,12,23,31,4,15,20,28,7,10,17,25,2,9,18,26,1],
                [0,28,29,1,31,3,2,30,27,7,6,26,4,24,25,5,19,15,14,18,12,16,17,13,8,20,21,9,23,11,10,22],
                [0,29,31,2,27,6,4,25,19,14,12,17,8,21,23,10,3,30,28,1,24,5,7,26,16,13,15,18,11,22,20,9],
                [0,30,25,7,23,9,14,16,11,21,18,12,28,2,5,27,22,8,15,17,1,31,24,6,29,3,4,26,10,20,19,13],
                [0,31,27,4,19,12,8,23,3,28,24,7,16,15,11,20,6,25,29,2,21,10,14,17,5,26,30,1,22,9,13,18]
                ]

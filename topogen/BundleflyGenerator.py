# Copyright (c) 2025 ETH Zurich.
#                    All rights reserved.
#
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# Main author: Kartik Lakhotia

from .TopologyGenerator import TopologyGenerator
from .validate_bundlefly import validate
from .SlimFlyGenerator import SlimFlyGenerator

import numpy as np

import itertools
import random
import networkx as nx
from sympy import symbols, Dummy
from sympy.polys.domains import ZZ
from sympy.polys.galoistools import (gf_irreducible_p, gf_add, gf_sub, gf_mul, gf_rem, gf_gcdex)
from sympy.ntheory.primetest import isprime
from functools import reduce


class GF():
    def __init__(self, p, n=1):
        p, n = int(p), int(n)
        if not isprime(p):
            raise ValueError("p must be a prime number, not %s" % p)
        if n <= 0:
            raise ValueError("n must be a positive integer, not %s" % n)
        self.p = p
        self.n = n
        if n == 1:
            self.reducing = [1, 0]
        else:
            for c in itertools.product(range(p), repeat=n):
                poly = (1, *c)
                if gf_irreducible_p(poly, p, ZZ):
                    self.reducing = poly
                    break
        self.elems = None
    
    def get_elems(self):
        if self.elems is None:
            self.elems = [[]]
            for c in range(1, self.p):
                self.elems.append([c])
            for deg in range(1,self.n):
                for c in itertools.product(range(self.p), repeat=deg):
                    for first in range(1, self.p):
                        self.elems.append(list((first, *c)))
            return self.elems
        else:
            return self.elems
    
    def get_primitive_elem(self):
        while True:
            primitive = random.choice(self.get_elems())
            if self.is_primitive_elem(primitive):
                return primitive

    def get_all_primitive_elems(self):
        return [elem for elem in self.get_elems() if self.is_primitive_elem(elem)]

    def is_primitive_elem(self, primitive) -> bool:
        elems = [[]]
        tmp = [1]
        for _ in range(1,self.p**self.n):
            tmp = self.mul(tmp,primitive)
            elems.append(tmp)

        if len(elems) == self.p**self.n and all(elem in elems  for elem in self.get_elems()):
            return True
        else:
            return False

    def add(self, x, y):
        return gf_add(x, y, self.p, ZZ)

    def sub(self, x, y):
        return gf_sub(x, y, self.p, ZZ)

    def mul(self, x, y):
        return gf_rem(gf_mul(x, y, self.p, ZZ), self.reducing, self.p, ZZ)

    def inv(self, x):
        s, t, h = gf_gcdex(x, self.reducing, self.p, ZZ)
        return s

    def eval_poly(self, poly, point):
        val = []
        for c in poly:
            val = self.mul(val, point)
            val = self.add(val, c)
        return val


class BundleflyGenerator(TopologyGenerator):
    def __init(self):
        super(BrownGenerator, self).__init__()

    def get_config(self, d):
        maxOrder    = 0
        maxmmsq     = 0
        maxpaleyq   = 0
        deltas      = [-1, 0, 1]
        for w in range(1,d):
            for delta in deltas:
                mmsq    = 4*w + delta
                if (not is_power_of_prime(mmsq)):
                    continue
                mmsradix    = (3*mmsq - delta)//2
                if (mmsradix >= d):
                    continue
                paleyradix  = d - mmsradix
                paleyq      = 2*paleyradix + 1
                if (not is_power_of_prime(paleyq)):
                    continue
                if (not (paleyq % 4 == 1)):
                    continue
                mmsorder    = 2*mmsq*mmsq
                bundleOrder = mmsorder*paleyq
                if (bundleOrder > maxOrder):
                    maxOrder    = bundleOrder
                    maxmmsq     = mmsq
                    maxpaleyq   = paleyq

        return maxOrder, maxmmsq, maxpaleyq

    def make(self, q : int):
        self.q  = q
        maxOrder, mmsq, paleyq   = self.get_config(q)
        if (maxOrder    == 0):
            return [[0]]
        paleyGraph, phi = paleyGen(paleyq)
        mmsGraph        = SlimFlyGenerator().make(mmsq)

        paleyV          = paleyGraph.number_of_nodes()
        mmsV            = len(mmsGraph)
        bundleV         = paleyV*mmsV

        graph           = [[] for _ in range(bundleV)]

        # intra-supernode edges
        for i in range(mmsV):
            for j in range(paleyV):
                u       = i*paleyV + j
                neighs  = [n for n in paleyGraph.neighbors(j)]
                for neigh in neighs:
                    v   = i*paleyV + neigh
                    graph[u].append(v)

        # inter-supernode edges
        for i in range(mmsV):
            for j in range(paleyV):
                u       = i*paleyV + j
                for k in mmsGraph[i]:
                    if (k > i):
                        v   = k*paleyV + phi[j]
                        graph[u].append(v)
                        graph[v].append(u)

        return graph

    def validate(self, topo : [[int]], q : int) -> bool:
        return validate(topo,q)

    def get_folder_path(self):
        return super(BundleflyGenerator,self).get_folder_path() + "bundleflies/"

    def get_file_name(self, q : int) -> str:
        return "Bundlefly." + str(q) + ".adj.txt"

############# Helper Functions ##############

def is_prime(num):
    for i in range(2,num):
        if ((num % i) == 0):
            return False
    return True

def is_power_of_prime(num):
    if (is_prime(num)):
        return True

    fact    = 2
    while(fact < num):
        rem = num%fact
        if (rem == 0):
            break
        else:
            fact += 1

    tmp     = num
    while(tmp>fact):
        if ((tmp%fact) > 0):
            return False
        else:
            tmp = tmp/fact
    return True

def get_power_of_prime(q):
    assert(is_power_of_prime(q))
    if (is_prime(q)):
        return q, 1
    else:
        fact    = 2
        while(fact < q):
            rem = q%fact
            if (rem == 0):
                break
            else:
                fact += 1
        tmp     = q
        power   = 0
        while (tmp >= fact):
            power   += 1
            tmp     = tmp/fact
        return fact,power
             
def print_graph(G):
    V   = list(G)
    for v in V:
        neigh   = [n for n in G.neighbors(v)]
        print(str(v) + "-> " + str(neigh))
            
def paleyGen(q):
    assert(q%4 == 1)

    prime, prime_power  = get_power_of_prime(q)

    gf  = GF(prime, prime_power)
    pe  = gf.get_primitive_elem()

    pe_powers   = [[1]]
    for i in range(1,q):
        pe_powers.append(gf.mul(pe_powers[i-1], pe)) 

    X   = [pe_powers[i] for i in range(0, q-2, 2)]
    XX  = [pe_powers[i] for i in range(1, q-1, 2)]        

    phi     = {}
    vertices= gf.get_elems()
    idx_map = {}

    for i in range(q):
        u   = vertices[i]
        for j in range(q):
            v   = vertices[j]
            if (gf.mul(u, pe) == v):
                assert(i not in phi)
                phi[i]  = j

    nx_graph    = nx.Graph() 
    nx_graph.add_nodes_from([i for i in range(0, q)])

    for i in range(q):
        for j in range(q):
            u   = vertices[i]
            v   = vertices[j]
            if (gf.sub(v,u) in X):
                nx_graph.add_edge(i, j)

    max_degree  = max(dict(nx_graph.degree).values())
    min_degree  = min(dict(nx_graph.degree).values())
    print("Paley : max degree = " + str(max_degree) + ", min degree = " + str(min_degree) + ", expected degree = " + str(int((q-1)/2)))

    return nx_graph, phi

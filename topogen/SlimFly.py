# Copyright (c) 2025 ETH Zurich.
#                    All rights reserved.
#
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# Main author: Alessandro Maissen

from .Topology import Topology
from .Jellyfish import Jellyfish
from .SlimFlyGenerator import SlimFlyGenerator
from .common import approx_inverse, is_prime, is_power_of_prime
from math import ceil


class SlimFly(Topology):
    """
    Fields:
        Public: 
            q: size of Galois field
            p: hosts per router
            nr: network radix of router 
            r: total radix of a router
            R: total number of routers
            N: total number of endnodes
            edge: number that indicates routers with endnodes (the first edge routers in topo have endnodes)
            delta: where q = 4w + delta
            w: where q = 4w + delta
            name: name of topology (default := SF)
        Private:
            __topo: holds None or the topology in adjacency list

    Methods: 
        get_topo(): return the topology in adjacency list
        get_jellyfish_eq(): return jellyfish topology that uses same infrastructure
    """

    def __init__(self, q = -1, N = -1):
        """
        Parameters:
            q: size of Galois field
            N: total number of endnodes

        Note: Only one of the parameters has to be specified for initialization.
        """

        if(q == -1 and N != -1):
            # find the lowest q of the three possibilites that support at least N endnodes
            candidate_q0 = approx_inverse(2*N, lambda q: q*q*(3*q))
            candidate_q1 = approx_inverse(2*N, lambda q: q*q*((3*q - 1)))
            candidate_q3 = approx_inverse(2*N, lambda q: q*q*((3*q + 1)))
            candidate_q = min([candidate_q0,candidate_q1,candidate_q3])

            # check form of q
            while not ((candidate_q % 4 == 1 or candidate_q % 4 == 3 or candidate_q % 4 == 0) and is_power_of_prime(candidate_q)):
                candidate_q += 1
        
            self.q = candidate_q
        elif(q != -1 and N == -1):
            self.q = q
        else:
            raise Exception("invalid combination of arguments in constructor")
        
        # setting delta based on q (q = 4w + delta, where delta = -1 0 1)
        if self.q % 4 == 3: 
            self.delta = -1
        elif self.q % 4 == 2:
            raise Exception("q is not of the form q:= 4w + delta")
        else: 
            self.delta = self.q % 4

        assert((self.q - self.delta) % 4 == 0)
        self.w = int((self.q - self.delta) / 4)
        assert(self.w >= 1)

        assert((3*self.q - self.delta) % 2 == 0)
        self.nr = int((3*self.q - self.delta)/2)
        self.p = ceil(self.nr / 2)
        self.r = self.p + self.nr
        self.R = 2*self.q**2
        self.N = self.p*self.R
        self.edge = self.R
        self.name = 'SF'

        # private fields
        self.__topo = None

    def get_topo(self):
        if self.__topo is None:
            self.__topo = SlimFlyGenerator().make(self.q)
        return self.__topo
    
    def get_jellyfish_eq(self):
        jf = Jellyfish(self.nr,self.R,self.p)
        jf.name += "-" + self.name
        return jf

# Copyright (c) 2025 ETH Zurich.
#                    All rights reserved.
#
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# Main author: Kartik Lakhotia

from .Topology import Topology
from .Jellyfish import Jellyfish
from .BundleflyGenerator import BundleflyGenerator
from .common import approx_inverse, is_prime, is_power_of_prime
from math import ceil


class Bundlefly(Topology):
    """
    Fields:
        Public: 
            q: degree 
        Private:
            __topo: holds None or the topology in adjacency list

    Methods: 
        get_topo(): return the topology in adjacency list
        get_jellyfish_eq(): return jellyfish topology that uses same infrastructure
    """

    def __init__(self, q = -1, N = -1):
        
        """
        Parameters:
            N: total number of endnodes

        Note: Only one of the parameters have to be specified for initialization.

        """

        if(q == -1 and N != -1):
            # find the lowest q of the three possibilites that support at least N endnodes
            candidate_q  = approx_inverse(4*N, lambda q: (q*q*q*q)/3)

            # check form of q
        
            self.q = candidate_q
        elif(q != -1 and N == -1):
            self.q = q
        else:
            raise Exception("invalid combination of arguments in constructor")
        
        # setting delta based on q (q = 4w + delta, where delta = -1 0 1)
        self.nr = self.q
        self.p  = self.nr//3
        self.r  = self.p + self.nr
        self.R, self.mmsq, self.paleyq = get_config(self.q)
        if (self.R == 0):
            raise Exception("bundlefly does not exist for this degree")
        self.N  = self.p*self.R
        self.edge   = self.R
        self.name   = 'BUNDLE'

        # private fields
        self.__topo = None

    def get_topo(self):
        if self.__topo is None:
            self.__topo = BundleflyGenerator().make(self.q)
        return self.__topo
    
    def get_jellyfish_eq(self):
        jf = Jellyfish(self.nr,self.R,self.p)
        jf.name += "-" + self.name
        return jf

############# Helper Functions ###############

def get_config(d):
     maxOrder    = 0
     maxmmsq     = 0
     maxpaleyq   = 0
     deltas  = [-1, 0, 1]
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

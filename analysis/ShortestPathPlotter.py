# Copyright (c) 2025 ETH Zurich.
#                    All rights reserved.
#
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# Main author: Jascha Krattenmacher

from .Plotter import Plotter
from .common import make_topos, find_runs
from .ShortestPathAnalysis import ShortestPathAnalysis
from .results import Results, pyplot 


class ShortestPathPlotter(Plotter):
    def __init__(self):
        super(ShortestPathPlotter,self).__init__()

    def plot_shortestpath_length(self, topos : [str], classes : [int], maxlength : int, jellyfish : bool, outfile = "plot.pdf", size = None, density=False):
        networks = make_topos(topos,classes,jellyfish)
        
        sh_analysis = ShortestPathAnalysis()
        sh_analysis.analyse(networks=networks, maxlength=maxlength, sparse=False)
        self.plotted_topologies_info(outfile,networks)
     
        res = Results(sh_analysis.datafile)

        runids = find_runs(networks,res,"shortest-path", maxlength)
        runids = "(" + ", ".join(str(x) for x in runids) + ")"

        runwhere = "runid in " + runids
        
        class_distinction = ""
        if len(classes) == 1:
            class_distinction = ' case when n_e < %d then %d else "" end ' %(10*classes[0], classes[0])
        elif len(classes) == 2:
            class_distinction = ' case when n_e < %d then %d else %d end ' %(classes[1], classes[0], classes[1])
        else:
            class_distinction = ' case when n_e < %d then %d' %(classes[1], classes[0])
            for i in range(1, len(classes) - 1):
                class_distinction += ' when n_e < %d then %d' %(classes[i+1],classes[i])
            class_distinction += ' else %d end '  %(classes[len(classes) - 1])

        select = 'len, case when topo like "JF-%" then substr(topo, 4) else topo end,' +class_distinction+ ', case when topo like "JF-%" then "eq. JF" else "base" end'

        where= 'len <=' + str(maxlength)

        if size is None:
            size = str((0.5+0.5*jellyfish+len(topos))*2.25) +"x" + str((1.5 + jellyfish)*2.25)

        pyplot(outfile=outfile, size=size, manual=False, datafile=sh_analysis.datafile, select=select, runwhere=runwhere, where=where, plotType = 'shortestpath_length', density=density, maxlength=maxlength, label='shortest path length $l_{min} \leq ' + str(maxlength) + '$', sqlLength=4, jellyfish=jellyfish, classes=classes)

    def plot_shortestpath_multiplicity(self, topos : [str], classes : [int], maxlength : int, maxmultiplicity : int, jellyfish : bool, outfile = "plot.pdf", size = None, density=False):
        networks = make_topos(topos,classes,jellyfish)
        
        sh_analysis = ShortestPathAnalysis()
        sh_analysis.analyse(networks=networks, maxlength=maxlength, sparse=False)
        self.plotted_topologies_info(outfile,networks)

        res = Results(sh_analysis.datafile)

        runids = find_runs(networks,res,"shortest-path", maxlength)
        runids = "(" + ", ".join(str(x) for x in runids) + ")"

        runwhere = "runid in " + runids

        class_distinction = ""
        if len(classes) == 1:
            class_distinction = ' case when n_e < %d then %d else "" end ' %(100*classes[0], classes[0])
        elif len(classes) == 2:
            class_distinction = ' case when n_e < %d then %d else %d end ' %(classes[1], classes[0], classes[1])
        else:
            class_distinction = ' case when n_e < %d then %d' %(classes[1], classes[0])
            for i in range(1, len(classes) - 1):
                class_distinction += ' when n_e < %d then %d' %(classes[i+1], classes[i])
            class_distinction += ' else %d end '  %(classes[len(classes) - 1])


        if maxmultiplicity == 3:
            label = "$(1, 2, \geq 3)$"
        elif maxmultiplicity > 3:
            label = "$(1, 2,..., \geq " + str(maxmultiplicity) + ")$"
        else:
            label = "$(1 , >= 2)$"
        
        label += ", where $l_{min} \leq " + str(maxlength) + "$"

        select = 'min(multiplicity, '+ str(maxmultiplicity) +'), case when topo like "JF-%" then substr(topo, 4) else topo end, case when topo like "JF-%" then "eq. JF" else "base" end,' + class_distinction
        where= 'len <=' + str(maxlength)

        if size is None:
            size = str((0.5+0.5*jellyfish+len(topos))*2.25) +"x" + str((1.5 + jellyfish)*2.25)
        pyplot(outfile=outfile, size=size, manual=False, datafile=sh_analysis.datafile, select=select, runwhere=runwhere, where=where, plotType='shortestpath_multiplicity', density=density, maxlength=maxlength, maxmultiplicity=maxmultiplicity, label='shortest path multiplicity $n_{min}$' + label, sqlLength=4, jellyfish=jellyfish, classes=classes)

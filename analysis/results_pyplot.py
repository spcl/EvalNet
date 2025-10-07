# Copyright (c) 2025 ETH Zurich.
#                    All rights reserved.
#
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# Main author: Jascha Krattenmacher

# Plot function

from .results import plotdata
from tempfile import NamedTemporaryFile
from sqlite3 import connect 
from matplotlib import pyplot as plt, cm, colorbar
from matplotlib.colors import ListedColormap, LinearSegmentedColormap, TwoSlopeNorm, LogNorm
from matplotlib.ticker import MaxNLocator,MultipleLocator, LogFormatterExponent, LogLocator
from matplotlib.offsetbox import AnchoredText
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np


def pyplot(outfile, size, manual, **kwargs):
    w, h = [float(x) for x in size.split("x", 1)]
    
    conn, sql = plotdata(**kwargs)
    # create temp DB and read values from database
    with NamedTemporaryFile(delete=not manual) as t:
        conn.execute("ATTACH DATABASE ? AS forPlot;", (t.name,))
        conn.execute("CREATE TABLE forPlot.data(%s);" % ", ".join("C" + str(i) for i in range(kwargs['sqlLength'])))
        conn.execute("INSERT INTO forPlot.data %s" % sql)
        conn.commit()
        conn = connect(t.name)

        # use ggplot style (size & general design)
        plt.style.use('ggplot')
        plt.rcParams["figure.figsize"] = (w,h)
        plt.rcParams["axes.facecolor"] = 'white'
        plt.rcParams["grid.color"] = '0.7'
        plt.rcParams["axes.edgecolor"] = 'black'
        plt.rcParams["axes.spines.top"] = False
        plt.rcParams["axes.spines.right"] = False
        plt.rcParams["xtick.labelsize"] = 6
        plt.rcParams["ytick.labelsize"] = 6

        DEFAULT_FILL = '0.2'    # Color of default bar plots
        
        density = kwargs['density']    # if false counts of values are shown, else percentage

        label = kwargs['label']
        l_min = kwargs['maxlength']

        if kwargs['plotType'] == 'shortestpath_multiplicity':
            n_min = kwargs['maxmultiplicity']
      
        jf = kwargs['jellyfish']

        if kwargs['plotType'] == 'shortestpath_multiplicity' or kwargs['plotType'] == 'shortestpath_length':
            classes = kwargs['classes']
            numClasses = len(classes)

        # shortest paths
        if kwargs['plotType'] in ('shortestpath_multiplicity','shortestpath_length') :
          
            # form:
            # data[i][j] is data-array for topology[i] of class[j], if jf, data[i] is data-array of topology[i], data[numPlots+i] is jf data of topology[i] 

            data = []

            topos = [t[0] for t in conn.execute("SELECT DISTINCT C1 from data;").fetchall()]
            topos.sort()
            numPlots = len(topos)

            for i in range(numPlots):
                t = topos[i]
                data.append([])
                for c in classes:
                    data[i].append(conn.execute("SELECT * FROM data WHERE C1 = '%s' AND (C3 = 'base' or C2 = 'base') AND (C2 = %i or C3 = %i);" %(t,c,c)).fetchall())

            if jf:
                for i in range(numPlots):
                    t = topos[i]
                    data.append([])
                    for c in classes:
                        data[numPlots+i].append(conn.execute("SELECT * FROM data WHERE C1 = '%s' AND (C3 = 'eq. JF' or C2 = 'eq. JF') AND (C2 = %i or C3 = %i);" %(t,c,c)).fetchall())

            if kwargs['plotType'] == 'shortestpath_length':
                rangeBin = l_min
            else:
                rangeBin = n_min

            if jf:
                fig, axs = plt.subplots(2,numPlots)
            else:
                fig, axs = plt.subplots(1,numPlots)
                axs = [axs]

            if numPlots == 1:
                axs = [axs]
                if jf:
                    # needed in order to not have to handle the single case with JF
                    axs = [[axs[0][0],None],[axs[0][1],None]]

            # predefine bins and colors for all plots
            bins = [num+.5 for num in range(rangeBin+1)]
            colors = [str(c) for c in np.linspace(0.0,0.7,num=numClasses)]
  
            for i in range(numPlots):
    
                # calculate data
                plotData = []
                plotDataJF = []

                for j in range(numClasses):
                    plotData.append([d[0] for d in data[i][j]])
                    if jf:
                        plotDataJF.append([d[0] for d in data[numPlots + i][j]])
              
                n = axs[0][i].hist(plotData,bins,density=density, histtype='bar', label=classes, align='mid', color=colors)[0]
                if jf:
                    nJF = axs[1][i].hist(plotDataJF,bins,density=density, histtype='bar', label=classes, align='mid', color=colors)[0]

                maxY = 0
                if numClasses == 1:           
                    for value in n:
                        if value > maxY:
                            maxY = value
                    if jf:
                        for value in nJF:
                            if value > maxY:
                                maxY = value
                else:
                    for row in n:
                        for value in row:
                            if value > maxY:
                                maxY = value
                    if jf:
                        for row in nJF:
                            if max(row) > maxY:
                                    maxY = max(row)

            # design

            # used in adjust_subplot in the end and to place some labels, titles etc.
            wspaceAdj = 0.1
            if jf:
                bottomAdj = 0.2
            else:
                bottomAdj = 0.3333

            for i in range(numPlots):
                
                #title
                axs[0][i].set_title(topos[i])
                
                # ticks and axis
                xTicks = [ k+1 for k in range(rangeBin) ]
                axs[0][i].yaxis.set_major_locator(LogLocator(numticks=10))
                axs[0][i].yaxis.set_minor_locator(LogLocator(base=10.0, subs=(5.0, 0.5,)))
                axs[0][i].grid(which='minor', linestyle='dotted')
                axs[0][i].set_xticks(xTicks)

                if jf:
                    axs[1][i].yaxis.set_major_locator(LogLocator(numticks=10))
                    axs[1][i].yaxis.set_minor_locator(LogLocator(base=10.0, subs=(5.0,0.5)))
                    axs[1][i].grid(which='minor', linestyle='dotted')
                    axs[1][i].set_xticks(xTicks)

                    if density:
                        axs[0][i].set_ylim([0.,1.])
                        axs[1][i].set_ylim([0.,1.])
                    else:
                        axs[0][i].set_ylim([0., maxY])
                        axs[1][i].set_ylim([0., maxY])
    
                    axs[0][0].set_xlim([0.5,rangeBin+0.5])
                    axs[1][0].set_xlim([0.5,rangeBin+0.5])
    
                    if density:
                        if kwargs['plotType'] == 'shortestpath_length':
                            axs[0][i].set_ylim([0.01, 1.])
                            axs[1][i].set_ylim([0.01, 1.])
                        else:
                            axs[0][i].set_ylim([0.001, 1.])
                            axs[1][i].set_ylim([0.001, 1.])
                    else:
                        axs[0][i].set_ylim([1., maxY])
                        axs[1][i].set_ylim([1., maxY])
    
                    axs[0][i].set_yscale('log',base=10, subs=[5])
                    axs[1][i].set_yscale('log',base=10, subs=[5])

                    if i > 0:
                        axs[0][i].set_yticklabels([])
                        axs[1][i].set_yticklabels([])
                else:
                    if density:
                        axs[0][i].set_ylim([0.,1.])
                    else:
                        axs[0][i].set_ylim([0., maxY])

                    axs[0][0].set_xlim([0.5,rangeBin+0.5])

                    if density:
                        if kwargs['plotType'] == 'shortestpath_length':
                            axs[0][i].set_ylim([0.01, 1.])
                        else:
                            axs[0][i].set_ylim([0.001, 1.])
                    else:
                        axs[0][i].set_ylim([1., maxY])

                    axs[0][i].set_yscale('log',subs=[5])

                    if i > 0:
                        axs[0][i].set_yticklabels([])

            # labels
            if jf:
                axs[0][numPlots-1].yaxis.set_label_position("right")
                axs[0][numPlots-1].set_ylabel('Default\nvariant', rotation=270, verticalalignment='bottom')
                axs[1][numPlots-1].yaxis.set_label_position("right")
                axs[1][numPlots-1].set_ylabel('equivalent\nJellyfish', rotation=270, verticalalignment='bottom')

            # legend
            h, l = axs[0][0].get_legend_handles_labels()

            legend = fig.legend(h,l, loc='center',ncol=numClasses, fontsize=7, title_fontsize=10, bbox_to_anchor=(0.5, bottomAdj/2))
            legend.set_title('N (#Servers)')

            # labels maual
            if density:
                fig.supylabel('fraction of router pairs (%)')
            else:
                fig.supylabel('count')

            if kwargs['plotType'] == 'shortestpath_length':
                fig.supxlabel('length of minimal paths l_min (a,b)')
            else:
                fig.supxlabel('diversity of minimal disjoint paths c_min (a,b)')

            fig.supxlabel(label)
            fig.tight_layout()
            plt.subplots_adjust(wspace=wspaceAdj, bottom=bottomAdj)
            plt.savefig(outfile)

        # interference_detail  
        elif kwargs['plotType'] == 'interference_detail':

            data = conn.execute("SELECT * FROM data;").fetchall()

            topos = [str(t[0]) for t in conn.execute("SELECT DISTINCT( C3 ) FROM data;").fetchall()] # order topologies manually if a specific order is wanted
            topos.sort()
            numPlots = len(topos)
            maxI = int(conn.execute("SELECT MAX(C0) FROM data;").fetchall()[0][0])
            fig, axs = plt.subplots(numPlots,l_min)

            if numPlots == 1:
                axs = [axs]

            ticks = [i*10 for i in range(int(maxI/10))]
            minorTicks = [i*10+5 for i in range(int(maxI/10))]

            # calculate values
            maxValue = 0
            data = [] #data[i][j] are the values of topos[i] of length j+1
            preset = 'l='
            bins = [i + 0.5 for i in range(maxI+1)]

            for i in range(numPlots):
                data.append([])
                for j in range(0,l_min):
                    data[i].append(conn.execute("SELECT C0,C1 FROM data WHERE C3 = '%s' AND C2 = '%s';" %(topos[i],preset+str(j+1))).fetchall())

            plotData=[]
            for i in range(numPlots):
                plotData.append([])
                for j in range(l_min):
                    x = [d[0] for d in data[i][j]]
                    y = [d[1] for d in data[i][j]]
                    h, xedges, yedges = np.histogram2d(x,y,bins=(bins,bins))
                    plotData[i].append(h)
                    for row in h:
                        for entry in row:
                            if maxValue < entry:
                                maxValue = entry

            # plot data
            for i in range(numPlots):
                for j in range(l_min):
                    # eliminate 0 values
                    h = np.ma.masked_array(plotData[i][j],plotData[i][j]<=0)
                    im = axs[i][j].imshow(h.T, cmap=cm.gray, interpolation='nearest', norm=LogNorm(vmin=1,vmax=maxValue), zorder=2)

            # design
            for i in range(numPlots):
                for j in range(l_min):
                    # ticks and ticklabels
                    axs[i][j].grid(which='minor', linestyle='dotted')
                    axs[i][j].xaxis.set_major_locator(MultipleLocator(10))
                    axs[i][j].xaxis.set_minor_locator(MultipleLocator(5))
                    axs[i][j].yaxis.set_major_locator(MultipleLocator(10))
                    axs[i][j].yaxis.set_minor_locator(MultipleLocator(5))
                    axs[i][j].set_xlim((-0.5,maxI+0.5))
                    axs[i][j].set_ylim((-0.5,maxI+0.5))
                    if j > 0:
                        axs[i][j].set_yticklabels([])
                    if i < numPlots-1:
                        axs[i][j].set_xticklabels([])

                axs[i][l_min-1].yaxis.set_label_position('right')
                axs[i][l_min-1].set_ylabel(topos[i], fontsize=14, rotation=270, verticalalignment='bottom')
               
            # labels 
            for j in range(0,l_min):
                axs[0][j].set_title(preset + str(j+1), fontsize=14)

            legendY = 0.333/(numPlots+1) 
            plt.subplots_adjust(hspace=0.1, wspace=0.1, top= 1-0.333/(numPlots+1), left=0.666/(l_min+1), right= 1 - 0.333/(l_min+1))
            fig.subplots_adjust(bottom=0.666/(numPlots+1)) 
            cb_ax = fig.add_axes([0.6,legendY , 0.2, 0.1/numPlots])
            cbar = fig.colorbar(im, cax=cb_ax,ax=axs[numPlots-1][:l_min], use_gridspec=True, shrink=0.25, location='bottom' )

            fig.supxlabel(label, x=0.3, y=legendY, va='center') 
            fig.supylabel('$c_l (\{a,c\}, \{b,d\})$', x=0.333/(l_min+1),y = 0.5, ha='left') 
            plt.savefig(outfile)

        # edge disjoint path and interference
        elif kwargs['plotType'] in ('edge_disjoint_path_count', 'interference'):
           
            # get data for multiple topologies
            topos = [str(t[0]) for t in conn.execute("SELECT DISTINCT( C2 ) FROM data;").fetchall()]
            topos.sort()
            numPlots = len(topos)
  
            data = [] # data[i][j] holds data of topo[i] and l=j+1
           
            for i in range(numPlots):
                t = topos[i]
                data.append([])
                for j in range(l_min):
                    data[i].append(conn.execute("SELECT C0 FROM data WHERE C2 = '%s' AND C1 = 'l=%i';" %(t, j+1)).fetchall())

            maxX = int(conn.execute("SELECT MAX(C0) FROM data;").fetchall()[0][0])
            maxY = 0

            # plot data
            fig, axs = plt.subplots(numPlots, l_min)
            bins = [num for num in range(maxX+1)]

            if numPlots == 1:
                axs = [axs]

            for i in range(numPlots):
                for j in range(l_min):
                     # use numpy histogram for performance reasons
                     h, edges = np.histogram(data[i][j],bins=bins, density=density)
                     for value in h:
                         if value > maxY:
                             maxY = value
                     
                     axs[i][j].bar(bins[:-1],h,color=DEFAULT_FILL)

            # design   
            preset = 'l='    
          
            for i in range(numPlots):
                for j in range(l_min):
                    # ticks and ticklabels
                    axs[i][j].xaxis.set_major_locator(MultipleLocator(5))
                    axs[i][j].xaxis.set_minor_locator(MultipleLocator(2.5))
                    axs[i][j].yaxis.set_major_locator(LogLocator(base=10.0, subs=(1,)))
                    axs[i][j].yaxis.set_minor_locator(LogLocator(base=10.0, subs=(5.0, 0.5)))
                    axs[i][j].grid(which='minor', linestyle='dotted')
                    axs[i][j].set_xlim((-0.5,maxX+0.5))
                    axs[i][j].set_yscale('log',subs=[5])

                    if density:
                        if kwargs['plotType'] == 'interference':
                            axs[i,j].set_ylim([10E-4,1.])
                        else:
                            axs[i,j].set_ylim([10E-5,1.])
                    else:
                        axs[i][j].set_ylim([1,maxY])

                    axs[i][j].set_xlim([-0.5,maxX+0.5])
                    if j > 0:
                        axs[i][j].set_yticklabels([])

                    if i < numPlots-1:
                        axs[i][j].set_xticklabels([])
                 
                # label
                axs[i][l_min-1].yaxis.set_label_position('right')
                axs[i][l_min-1].set_ylabel(topos[i], fontsize=14, rotation=270, verticalalignment='bottom')

            for j in range(l_min):
                axs[0][j].set_title(preset + str(j+1), fontsize=14)

            # label (manual)
            fig.supxlabel(label)

            if density:
                fig.supylabel('fraction of router pairs (%)')
            else:
                fig.supylabel('count')

            fig.tight_layout()
            fig.subplots_adjust(hspace=0.1, wspace=0.1)
            plt.savefig(outfile)
                
        # low connectivity
        elif kwargs['plotType'] == "low_connectivity": 
          
            DETAILED_TICKS = not kwargs['detailedTicks']     # if true, shows exact value of connectivity percentage on legend
            NORMALIZED_SCALE = not kwargs['normalizedScale'] # if true, shows legend (colorbar) from 0 to 1, instead of only showing range of connectivity percentages

            plt.rcParams["xtick.labelsize"] = 10
            plt.rcParams["ytick.labelsize"] = 10

            # get data
            data = conn.execute("SELECT * FROM data;").fetchall()

            # collect variables
            try:
                maxId = int(conn.execute("SELECT MAX(C0) FROM data;").fetchall()[0][0]) +1
            except:
                print("no values found for %s" %label)
                return

            plotEdge = np.empty((maxId,maxId))
            plotPath = np.empty((maxId,maxId))
            plotEdge[:] = -1
            plotPath[:] = -1
            specificTicksEdge = []
            specificTicksPath = []
            specificTickLabelsEdge = []
            specificTickLabelsPath = []

            # prepare data for plot
            for d in data:
                value = float(d[2].rstrip(d[2][-1]))/100
                if d[4] == 'Path':
                    plotPath[d[0],d[1]] = value
                    if value not in specificTicksPath:
                        specificTicksPath.append(value)
                        specificTickLabelsPath.append(d[2])
                else:
                    plotEdge[d[0],d[1]] = value
                    if value not in specificTicksEdge:
                        specificTicksEdge.append(value)
                        specificTickLabelsEdge.append(d[2])

            fig, ax = plt.subplots()

            plotPath = np.ma.masked_array(plotPath,plotPath<=0)
            plotEdge = np.ma.masked_array(plotEdge, plotEdge<=0)

            if NORMALIZED_SCALE:
                pa = ax.imshow(plotPath,interpolation='nearest',cmap=cm.Reds, vmin=0., vmax=1.)
            else:
                pa = ax.imshow(plotPath,interpolation='nearest',cmap=cm.Reds)

            pb = ax.imshow(plotEdge,interpolation='nearest',cmap=cm.winter, vmin=0., vmax=1.)

            # design
            ax.grid(False)
            ax.spines[['right', 'left', 'top', 'bottom']].set_visible(False)

            # ticks and ticklabels
            cbarTicksEdge = specificTicksEdge
            cbarTickLabelsEdge = specificTickLabelsEdge

            if DETAILED_TICKS:
                cbarTicksPath = specificTicksPath
                cbarTickLabelsPath = specificTickLabelsPath
            else:
                cbarTicksPath = [0., 0.2 , 0.4, 0.6, 0.8, 1.]
                cbarTickLabelsPath = ['0%', '20%', '40%', '60%', '80%', '100%']

            # colorbar
            if specificTicksPath and specificTicksEdge and l_min != 1:
                adjustRight = 0.85
                adjustBottom = 0.175
                cb_ax_path = fig.add_axes([0.929,0.36875, 0.02, 0.3875])
                cb_ax_edge = fig.add_axes([0.859,0.36875, 0.02, 0.3875])
            else:
                adjustRight = 0.9 
                adjustBottom = 0.15
                if specificTicksPath and l_min != 1:
                    cb_ax_path = fig.add_axes([0.909,0.35, 0.02, 0.4])
                elif specificTicksEdge:
                    cb_ax_edge = fig.add_axes([0.909,0.35, 0.02, 0.4])
                else:
                    print("error, no data")

            if specificTicksPath and l_min != 1:
                cbPath = plt.colorbar(pa,cax=cb_ax_path,ticks=cbarTicksPath)
                cbPath.ax.set_yticklabels(cbarTickLabelsPath, fontsize=7, rotation=-45)

                if not DETAILED_TICKS:
                    for value in specificTicksPath:
                        cbPath.ax.plot([0, 1], [value,value], 'w')

                cbPath.ax.set_title('Path', fontsize=10)
                cbPath.ax.spines[['right', 'left', 'top', 'bottom']].set_visible(False)

            if specificTicksEdge:
                cbEdge = plt.colorbar(pb,cax=cb_ax_edge, ticks=cbarTicksEdge)
                cbEdge.ax.set_yticklabels(cbarTickLabelsEdge, fontsize=7, rotation=-45)

                cbEdge.ax.set_title('Edge', fontsize = 10)
                cbEdge.ax.spines[['right', 'left', 'top', 'bottom']].set_visible(False)

            # labels
            ax.set_title(data[0][3])
            ax.set_ylabel('t')
            ax.set_xlabel('s\n\n' + label)

            plt.tight_layout
            fig.subplots_adjust(left=0.075, right = adjustRight, bottom=adjustBottom, top=0.95)
            plt.savefig(outfile)
        else:
            raise Exception('invalid analysis')

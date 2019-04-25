""" LPWAN Simulator: Hepper functions
============================================
Utilities (:mod:`lorawan.plotting`)
============================================
.. autosummary::
   :toctree: generated/
   plotSensitivity      -- sensitivity vs bandwidth
   plotAirtime          -- airtime vs sf and bandwidth
   plotLocations        -- location
   plotMaxDistFig       -- max distance

With some codes from extended LoRaSim library: https://github.com/adwaitnd/lorasim

"""
# Import Library
from numpy import zeros
import matplotlib.pyplot as plt
from .loratools import airtime
from matplotlib.lines import Line2D

__all__ = ['label', 'plotSensitivity', 'plotAirtime', 'plotLocations', 'plotMaxDistFig']

def label(xy, text):
    """ 
    Label the location of each device
    Parameters
    ----------
    xy : array
        Position of the device.
    text: text string
        Label    
    Returns
    -------
    """
    y = xy[1] + 30  # shift y-value for label so that it's below the artist
    plt.text(xy[0], y, text, ha="center", family='sans-serif', size=10)
    
def plotSensitivity(sensi):
    """
    Plot the sensitivity for some bandwidths.
    Parameters
    ----------
    sensi : matrix
        Correspoding sensitiviies for each bandwidth.
    Returns
    -------
    """
    fig, sensi_fig = plt.subplots(figsize=(12,6))

    s125, = sensi_fig.plot(sensi[:,0], sensi[:,1],"bo-", label="125 kHz")
    s250, = sensi_fig.plot(sensi[:,0], sensi[:,2],"ko:", label="250 kHz")
    s500, = sensi_fig.plot(sensi[:,0], sensi[:,3],"ro--", label="500 kHz")

    plt.legend(title="Bandwidth", handles = [s125, s250, s500])
    plt.grid()
    plt.xlabel("Spreading Factor (2^)")
    plt.ylabel("Base-station Receiver\nSensitivity (dBm)")
    plt.xticks([7, 8, 9, 10, 11, 12])

    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.size"] = 16
    plt.show()

def plotAirtime(phyParams):
    """
    Plot the time of air for some bandwidths and spreading factors.
    Parameters
    ----------
    phyParams: array
        Physical parameters.
    Returns
    -------
    """
    rdd, packetLength, preambleLength, syncLength, headerEnable, crc = phyParams
    bw_list = [125, 250, 500]
    sf_list = [7, 8, 9, 10, 11, 12]
    
    time_in_air = zeros((len(bw_list), len(sf_list)))
    
    for i,bw in enumerate(bw_list):
        for j,sf in enumerate(sf_list):
            time_in_air[i,j] = airtime((sf, rdd, bw, packetLength, preambleLength, syncLength, headerEnable, crc))
            
    fig, airtime_fig = plt.subplots(figsize=(12,6))
    
    at125, = airtime_fig.plot(sf_list, time_in_air[0,:], "bo-", label="125 kHz")
    at250, = airtime_fig.plot(sf_list, time_in_air[1,:], "ko:", label="250 kHz")
    at500, = airtime_fig.plot(sf_list, time_in_air[2,:], "ro--", label="500 kHz")

    plt.legend(title="Bandwidth", handles = [at125, at250, at500])
    plt.grid()
    plt.xlabel("Spreading Factor")
    plt.ylabel("Packet Airtime (ms)")
    plt.xticks([7, 8, 9, 10, 11, 12])

    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.size"] = 16
    
    plt.show()

def plotLocations(BSLoc, nodeLoc, maxX, maxY, bestDist, distMatrix):
    """
    Plot the location of the nodes and BS in the network.
    Parameters
    ----------
    BSLoc: array
        Location of BS.
    nodeLoc: array
        Location of node.
    maxX: float
        maximum distance in x-axis.
    maxY: float
        maximum distance in y-axis.
    bestDist: float
        best distance.
    distMatrix: array of floats
        distance matrix.
    Returns
    -------
    """
    fig, loc_plot = plt.subplots(figsize=(12,12))
    loc_ax = plt.gca()
    color = ['gray', 'gray', 'gray', 'gray', 'gray', 'gray']
    #legend_elements = [Line2D([0], [0],marker='o', color='w', label='Normal end-device'     , markerfacecolor='g', markersize=15),
    #                   Line2D([0], [0],marker='s', color='w', label='Inteligent end-device' , markerfacecolor='b', markersize=15),
    #                   Line2D([0], [0],marker='^', color='w', label='Gateway'               , markerfacecolor='c', markersize=15)]
    for b in BSLoc[:,1:3]:
        # draw the circle for each SF
        for i in range(len(distMatrix)):
           loc_ax.add_artist(plt.Circle((b[0], b[1]), distMatrix[i], fill=False, hatch=None, color = color[i])) 
    for i in range(0,len(nodeLoc)):
        if nodeLoc[i,13] == 0:
            nodePoints = loc_plot.plot(nodeLoc[i,1], nodeLoc[i,2], "ro", mfc='none', label="Normal end-device") # , label="normal node")
        else:
            nodePoints = loc_plot.plot(nodeLoc[i,1], nodeLoc[i,2], "ro", mfc='none', label="Inteligent end-device") #, label="intelligent node")
    for i in range(0,len(nodeLoc)):
        label((nodeLoc[i, 1], nodeLoc[i, 2]), str(i))
    
    bsPoints = loc_plot.plot(BSLoc[:,1], BSLoc[:,2], "^", label="gateway")
    
    # more nodes/BSs
    #nodePoints1, = plt.plot(nodeLoc[0:(nrNodes/2),1], nodeLoc[0:(nrNodes/2),2], "b.", mfc='none', label="Network 0\nEnd Device")
    #nodePoints2, = plt.plot(nodeLoc[(nrNodes/2):,1], nodeLoc[(nrNodes/2):,2], "g.", mfc='none', label="Network 1\nEnd Device")
    #bsPoints1, = plt.plot(BSLoc[0,1], BSLoc[0,2], "b^", label="Network 0\nBase Station", markersize=12, markeredgecolor='k')
    #bsPoints2, = plt.plot(BSLoc[1,1], BSLoc[1,2], "g^", label="Network 1\nBase Station", markersize=12, markeredgecolor='k')
    
    plt.xticks([0, 5000, 10000, 15000, 20000], [0,5,10,15,20])
    plt.yticks([0, 5000, 10000, 15000, 20000], [0,5,10,15,20])
    
    
#    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.grid()
    
    plt.axis('equal')
    plt.xlim((0, maxX))
    plt.ylim((0, maxY))
    
    plt.xlabel('distance (km)')
    plt.ylabel('distance (km)')
    
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.size"] = 12

    # plt.tight_layout()
    # plt.savefig('CompetitionLayout.pdf', format='pdf', bbox_extra_artists=(lgd,), bbox_inches='tight')
    
    plt.show()
    
def plotMaxDistFig(sensi, maxDist):
    """
    Plot the max distance for some bandwidths.
    Parameters
    ----------
    sensi: matrix
        sentitivity table.
    maxDist: matrix
        max distance table.
    Returns
    -------
    """
    fig, maxDist_fig = plt.subplots(figsize=(12,6))
    maxDist_fig.plot(sensi[:,0], maxDist[:,0], 'b', label="125 kHz")
    maxDist_fig.plot(sensi[:,0], maxDist[:,1], 'k', label="250 kHz")
    maxDist_fig.plot(sensi[:,0], maxDist[:,2], 'r', label="500 kHz")
    plt.show()
    
def plotPacketReception(simSetting, successRatio):
    """
    Plot the packet reception rate for simulation setting.
    Parameters
    ----------
    simSetting: array
        simulation setting.
    nRecvd: array
        number of received packets.
    Returns
    -------
    """
    fig, aimDerPlot = plt.subplots(figsize=(12,6))
    aimDerPlot.plot(simSetting, successRatio, 'bo-')
    
    plt.xlabel("Number of nodes")
    plt.ylabel("Packet reception rate")
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.size"] = 16
    
    plt.show()

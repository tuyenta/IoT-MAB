""" LPWAN Simulator: Hepper functions
    ============================================
    Utilities (:mod:`lora.utils`)
    ============================================
    .. autosummary::
    :toctree: generated/
    print_params             -- Print the arguments of the simulation.
    sim                      -- Run the simulation
    """
import os
import numpy as np
from os.path import join, exists
from os import makedirs
import simpy
import pandas as pd
import matplotlib.pyplot as plt
from .node import myNode
from .bs import myBS
from .bsFunctions import transmitPacket, cuckooClock, saveProb
from .loratools import dBmTomW, getMaxTransmitDistance, placeRandomlyInRange, placeRandomly
from .plotting import plotLocations

def print_params(nrNodes, nrIntNodes, nrBS, radius, avgSendTime, horTime, packetLength, sfSet, freqSet, powSet, captureEffect, interSFInterference, info_mode):
    # print parametters
    print("Simulation Parameters:")
    print ("\t Nodes:",nrNodes)
    print ("\t Intelligent Nodes:",nrIntNodes)
    print("\t BS:",nrBS)
    print("\t Radius:", radius)
    print ("\t AvgSendTime (exp. distributed):",avgSendTime)
    print ("\t Horizon Time:",horTime)
    print("\t Packet lengths:",packetLength)
    print("\t SF set:",sfSet)
    print("\t Channels: ",freqSet)
    print("\t Power set[dB]:",powSet)
    print ("\t Capture Effect:",captureEffect)
    print ("\t Inter-SF Interference:",interSFInterference)
    print ("\t Information mode:",info_mode)

def sim(nrNodes, nrIntNodes, nrBS, radius, avgSendTime, horTime, packetLength, sfSet, freqSet,
        powSet, captureEffect, interSFInterference, info_mode, logdir, exp_name) :
    
    simtime = horTime * avgSendTime # simulation time in ms
    
    grid = [10000, 10000] # maximum simulation area in m
    
    # Node parameters
    ackLength = 8 # length of the ack
    maxPtx = max(powSet)
    
    # phy parameters (rdd, packetLength, preambleLength, syncLength, headerEnable, crc)
    phyParams = (1, packetLength, 8, 4.25, False, True)
    
    # Environement parameters (Log-shadowing model)
    logDistParams=(2.08, 107.41, 40.0) # (gamma, Lpld0, d0)
    interferenceThreshold = -150 # dBm
    
    # BS parameters
    nDemodulator = 8 # number of demodulators on base-station
    
    # sensitivity
    sf7  = np.array([7, -124.5,-121.5,-118.5])
    sf8  = np.array([8, -127.0,-124.0,-121.0])
    sf9  = np.array([9, -129.5,-126.5,-123.5])
    sf10 = np.array([10,-132.0,-129.0,-126.0])
    sf11 = np.array([11,-134.5,-131.5,-128.5])
    sf12 = np.array([12,-137.0,-134.0,-131.0])
    sensi = np.array([sf7,sf8,sf9,sf10,sf11,sf12]) # array of sensitivity values
    
    # The spreading factor interaction matrix derived from lab tests and Semtech documentation
    # SFs are not perfectly orthogonal: a signal at SF_m faces interferences from all signals on other SFs
    if captureEffect == True:
        captureThreshold = dBmTomW(6) # threshold is 6 dB
        if interSFInterference == True:
            interactionMatrix = np.array([
                                          [dBmTomW(6), dBmTomW(-7), dBmTomW(-7), dBmTomW(-7), dBmTomW(-7), dBmTomW(-7)],
                                          [dBmTomW(-10), dBmTomW(6), dBmTomW(-10), dBmTomW(-10), dBmTomW(-10), dBmTomW(-10)],
                                          [dBmTomW(-12.5), dBmTomW(-12.5), dBmTomW(6), dBmTomW(-12.5), dBmTomW(-12.5), dBmTomW(-12.5)],
                                          [dBmTomW(-15), dBmTomW(-15), dBmTomW(-15), dBmTomW(6), dBmTomW(-15), dBmTomW(-15)],
                                          [dBmTomW(-17.5), dBmTomW(-17.5), dBmTomW(-17.5), dBmTomW(-17.5), dBmTomW(6), dBmTomW(-17.5)],
                                          [dBmTomW(-20), dBmTomW(-20), dBmTomW(-20), dBmTomW(-20), dBmTomW(-20), dBmTomW(6)]])
        else:
            interactionMatrix = np.array([
                                          [dBmTomW(6), 0,          0,             0,          0,          0         ],
                                          [0,          dBmTomW(6), 0,             0,          0,          0         ],
                                          [0,          0         , dBmTomW(6),    0,          0,          0         ],
                                          [0,          0         , 0,             dBmTomW(6), 0,          0         ],
                                          [0,          0         , 0,             0,          dBmTomW(6), 0         ],
                                          [0,          0         , 0,             0,          0,          dBmTomW(6)]])
else:
    captureThreshold = 0 # threshold is 0
        interactionMatrix = np.eye(len(sfSet), dtype=int)

    # Location generator
    print ("======= Generate/Load simulation scenario =======")
    distMatrix, bestDist, bestSF, bestBW = getMaxTransmitDistance(sensi, maxPtx, logDistParams, phyParams)
    print ("Max range = {} at SF = {}, BW = {}".format(bestDist, bestSF, bestBW))

# Generate base station and nodes
np.random.seed(12345) # seed the random generator

    # Place base-stations randomly
    simu_dir = join('logs', exp_name)
    #make folder
    if not exists(simu_dir):
        makedirs(simu_dir)
file_1 = join(simu_dir, "bsList_bs" + str(nrBS) + "_nodes" + str(nrNodes) + ".npy")
file_2 = join(simu_dir, "nodeList_bs"+ str(nrBS) + "_nodes" + str(nrNodes) + ".npy")

    if not os.path.exists(file_1):
        if not os.path.exists(file_2):
            print ("Generated locations for {} base-stations and {} nodes".format(nrBS, nrNodes))
            BSLoc = np.zeros((nrBS, 3))
            if nrBS == 1:
                BSLoc[0] = [0, grid[0]*0.5, grid[1]*0.5]
            else:
                placeRandomly(nrBS, BSLoc, [grid[0]*0.1, grid[0]*0.9], [grid[1]*0.1, grid[1]*0.9])
            
            # Place nodes randomly
            nodeLoc = np.zeros((nrNodes, 14))
            placeRandomlyInRange(nrNodes, nrIntNodes, nodeLoc, [0, grid[0]], [0, grid[1]], BSLoc, (bestDist, bestSF, bestBW), radius, phyParams, maxPtx, avgSendTime)
            
            # save to file
            np.save(file_1, BSLoc)
            np.save(file_2, nodeLoc)
else:
    # Load =location
    print ("\t Load locations for {} base-stations and {} nodes".format(nrBS, nrNodes))
    BSLoc = np.load(file_1)
    nodeLoc = np.load(file_2)
    
    # Simulation
    nTransmitted = 0
    nRecvd = 0
    
    BSList = BSLoc[0:nrBS,:]
    nodeList = nodeLoc[0:nrNodes,:]
    nodeList[0:nrIntNodes, -1] = 1 # Intelligent nodes
    print ("=============== Setup parameters ================")
    print ("# base-stations = {}".format(nrBS))
    print ("# nodes = {}".format(nrNodes))
    #fname = 'prob_'
    
    env = simpy.Environment()
    env.process(cuckooClock(env))
    
    fname = 'prob_'+ str(nrIntNodes) +'_smartNodes_' + 'infoMode_' + str(info_mode) + '_captureEffect_' + str(captureEffect) + '_interSFMode_' + str(interSFInterference)
    
    bsDict = {} # setup empty dictionary for base-stations
    for elem in BSList:
        bsDict[int(elem[0])] = myBS(int(elem[0]), (elem[1], elem[2]), interactionMatrix, nDemodulator, ackLength, freqSet, sfSet, captureThreshold)

    nodeDict = {} # setup empty dictionary for nodes
    for elem in nodeList:
        node = myNode(int(elem[0]), (elem[1], elem[2]), elem[3:13], sfSet, freqSet, powSet, BSList, interferenceThreshold, logDistParams,
                      sensi, elem[13], info_mode, horTime)
                      nodeDict[node.nodeid] = node
                      env.process(transmitPacket(env, node, bsDict, logDistParams))

# compute traffic
env.process(saveProb(env, nodeDict, fname, simu_dir))
env.run(until=simtime)

    # reception
    for nodeid, node in nodeDict.items():
        nTransmitted += node.packetsTransmitted
        nRecvd += node.packetsSuccessful

# print results
print ("================== Results ==================")
print ("# Transmitted = {}".format(nTransmitted))
print ("# Received = {}".format(nRecvd))
print ("# Ratio = {}".format(nRecvd/nTransmitted))

    # Plotting - location
    #plotLocations(BSLoc, nodeLoc, grid[0], grid[1], bestDist, distMatrix)
    
    # save and plot data
    probDict = {}
    for nodeid in range(nrIntNodes):
        filename = join(simu_dir, str(fname) + '_id_' + str(nodeid) + '.csv')
        df = pd.read_csv(filename, delimiter=' ', header= None, index_col=False)
        df = df.replace(',', '', regex=True).astype('float64').values
        
        fig, ax = plt.subplots(figsize=(8,5))
        for idx in range(df.shape[1]):
            ax.plot(df[:,idx], label = 'SF = {}'.format(12-df.shape[1]+idx+1))
            plt.xlabel("Horizon time")
            plt.ylabel("Probability")
            ax.legend(loc='best')
            plt.rcParams["font.family"] = "sans-serif"
            plt.rcParams["font.size"] = 16
            plt.close(fig)
        # save to file
        fig.savefig(join(simu_dir, str(fname) + '_id_' + str(nodeid) + '.png'))
        # probDict
        probDict[nodeid] = df[-1 , :]
    # save probDict
    np.save(join(simu_dir, str(fname)), probDict)

    return(bsDict, nodeDict)

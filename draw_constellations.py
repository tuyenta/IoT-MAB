#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 14:12:22 2019

@author: tuyenta
"""
import numpy as np
from os.path import join, exists
from os import makedirs
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from lora.loratools import getMaxTransmitDistance

nrNodes = int(100)
nrIntNodes = int(100)
nrBS = int(1)
initial = "UNIFORM"
radius = float(4000)
avgSendTime = int(4*60*1000)
horTime = int(1e7)
packetLength = int(50)
sfSet = [7, 8, 9, 10, 11, 12]
freqSet = [867300]
powSet = [14]
captureEffect = True
interSFInterference = True
info_mode = 'NO'
maxX = 10000
maxY = 10000

ackLength = 8 # length of the ack
maxPtx = max(powSet)
phyParams = (1, packetLength, 8, 4.25, False, True)

# Environement parameters (Log-shadowing model)
logDistParams=(2.08, 107.41, 40.0) # (gamma, Lpld0, d0)
interferenceThreshold = -150 # dBm

# sensitivity
sf7  = np.array([7, -123.0,-121.5,-118.5])
sf8  = np.array([8, -126.0,-124.0,-121.0])
sf9  = np.array([9, -129.5,-126.5,-123.5])
sf10 = np.array([10,-132.0,-129.0,-126.0])
sf11 = np.array([11,-134.5,-131.5,-128.5])
sf12 = np.array([12,-137.0,-134.0,-131.0])
sensi = np.array([sf7,sf8,sf9,sf10,sf11,sf12]) # array of sensitivity values

distMatrix, bestDist, bestSF, bestBW = getMaxTransmitDistance(sensi, maxPtx, logDistParams, phyParams)

#make folder
exp_name = 'exp2_100nodes'
logdir = 'Sim_1'

simu_dir = join(logdir, exp_name)
if not exists(simu_dir):
    makedirs(simu_dir)
file_1 = join(logdir, "bsList_bs" + str(nrBS) + "_nodes" + str(nrNodes) + ".npy")
file_2 = join(logdir, "nodeList_bs"+ str(nrBS) + "_nodes" + str(nrNodes) + ".npy")

BSLoc = np.load(file_1)
nodeLoc = np.load(file_2)

fig, loc_plot = plt.subplots(figsize=(12,12))
loc_ax = plt.gca()
color = ['gray', 'gray', 'gray', 'gray', 'gray', 'gray']
marker = ['g+', 'bo', 'c*', 'yp', 'ms', 'rD']
legend_elements = [Line2D([0], [0],marker='+', color='w', label='SF 7' , markerfacecolor='g', markersize=15),
                   Line2D([0], [0],marker='o', color='w', label='SF 8' , markerfacecolor='b', markersize=15),
                   Line2D([0], [0],marker='*', color='w', label='SF 9' , markerfacecolor='c', markersize=15),
                   Line2D([0], [0],marker='p', color='w', label='SF 10', markerfacecolor='y', markersize=15),
                   Line2D([0], [0],marker='s', color='w', label='SF 11', markerfacecolor='m', markersize=15),
                   Line2D([0], [0],marker='D', color='w', label='SF 12', markerfacecolor='r', markersize=15),
                   Line2D([0], [0],marker='^', color='w', label='GW',    markerfacecolor='c', markersize=15)]
                   
for b in BSLoc[:,1:3]:
    for i in range(len(distMatrix)):
       loc_ax.add_artist(plt.Circle((b[0], b[1]), distMatrix[i], fill=False, hatch=None, color = color[i])) 

for i in range(0,len(nodeLoc)):     
    dist = np.sqrt((nodeLoc[i,1] - BSLoc[0, 1])**2 + (nodeLoc[i,2] - BSLoc[0, 2])**2)
    for j in range(6):
        if i in [91, 99, 21, 46]:
            loc_plot.plot(nodeLoc[i,1], nodeLoc[i,2], "bo", markeredgewidth=2, markersize=15, label = 'SF 8')
        else:
            if dist <= distMatrix[0]:
                loc_plot.plot(nodeLoc[i,1], nodeLoc[i,2], marker[0], markeredgewidth=2, markersize=15, label = 'SF 7')   
            elif distMatrix[j] <= dist < distMatrix[j+1]:
                loc_plot.plot(nodeLoc[i,1], nodeLoc[i,2], marker[j+1], markeredgewidth=2, markersize=15, label = 'SF '+str(j+1+7))   

bsPoints = loc_plot.plot(BSLoc[:,1], BSLoc[:,2], "c^", markeredgewidth=2, markersize=15)

plt.xticks([0, 5000, 10000, 15000, 20000], [0,5,10,15,20])
plt.yticks([0, 5000, 10000, 15000, 20000], [0,5,10,15,20])


loc_plot.legend(handles=legend_elements, loc='lower left')
plt.grid()

plt.axis('equal')
plt.xlim((0, maxX))
plt.ylim((0, maxY))

plt.xlabel('distance (km)')
plt.ylabel('distance (km)')

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.size"] = 16
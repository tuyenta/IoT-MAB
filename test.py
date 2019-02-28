#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 14:05:43 2019

@author: tuyenta
"""
from lora.utils import print_params, sim

from os.path import join
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


nrNodes = int(5)
nrIntNodes = int(5)
nrBS = int(1)
radius = float(2000)
avgSendTime = int(360000)
horTime = int(1e1)
packetLength = int(50)
sfSet = [7, 8]
freqSet = [867100]
powSet = [14]
captureEffect = True
interSFInterference = True
info_mode = 'NO'

#make folder
exp_name = 'exp1'
logdir = 'logs'


# print simulation parameters
print("\n=================================================")
print_params(nrNodes, nrIntNodes, nrBS, radius, avgSendTime, horTime, packetLength, 
            sfSet, freqSet, powSet, captureEffect, interSFInterference, info_mode)

# running simulation
bsDict, nodeDict = sim(nrNodes, nrIntNodes, nrBS, radius, avgSendTime, 
                                horTime, packetLength, sfSet, freqSet, powSet, 
                                captureEffect, interSFInterference, info_mode, logdir, exp_name)

# save and plot data
fname = 'prob_'+ str(nrIntNodes) +'_smartNodes_' + 'infoMode_' + str(info_mode) + '_captureEffect_' + str(captureEffect) + '_interSFMode_' + str(interSFInterference)
simu_dir = join('logs', exp_name)
probDict = {}
for nodeid in range(nrIntNodes):
    filename = join(simu_dir, str(fname) + '_id_' + str(nodeid) + '.csv')
    df = pd.read_csv(filename, delimiter=' ', header= None, index_col=False)
    df = df.replace([',','}'], ['',''], regex=True)
        
    drop_list = []
    for i in range(df.shape[1]):
        if (i%2 == 0):
            drop_list.append(i)
    df = df.drop(drop_list, axis=1).astype('float64').values

    
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
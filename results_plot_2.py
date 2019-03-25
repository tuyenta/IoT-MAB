#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 13:37:46 2019

@author: tuyenta
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from os.path import join

# args
nrNodes = int(100)
nrIntNodes_list = [0, 0, 50, 50, 100, 100]
nrBS = int(1)
initial_list = ["RANDOM", "UNIFORM"]
radius = float(4500)
avgSendTime = int(240000)
horTime = int(1e7)
packetLength = int(50)
sfSet = [7, 8, 9, 10, 11, 12]
freqSet = [868100] #[868100, 868300, 868500]
powSet = [14] #[2, 5, 8, 11, 14]
captureEffect_list = [True]
interSFInterference_list = [True]
info_mode = 'NO'

#make folder
exp_name_list = ['0node_UNIFORM', '0node_RANDOM', '50nodes_UNIFORM', '50nodes_RANDOM', '100nodes_UNIFORM', '100nodes_RANDOM']
logdir = 'Sim_1'
#fig1, ax1 = plt.subplots(figsize=(12,10))
fig2, ax2 = plt.subplots(figsize=(12,10))

for idx in range(len(nrIntNodes_list)):
    nrIntNodes = nrIntNodes_list[idx]
    exp_name = exp_name_list[idx]
    simu_dir = join(logdir, exp_name)

    for captureEffect in captureEffect_list:
        for interSFInterference in interSFInterference_list:
            
            if idx%2 == 0:
                initial = "UNIFORM"
            else:
                initial = "RANDOM"
                
            fname = str(nrIntNodes) +'_smartNodes_' + 'initial_' +str(initial) + '_infoMode_' + str(info_mode) + '_captureEffect_' + str(captureEffect) + '_interSFMode_' + str(interSFInterference)
            filename_1 = join(simu_dir, str('ratio_'+ fname) + '.csv')
            filename_2 = join(simu_dir, str('traffic_'+ fname) + '.csv')
            filename_3 = join(simu_dir, str('energy_'+ fname) + '.csv')
            df_1 = pd.read_csv(filename_1, delimiter=' ', header= None, index_col=False).astype('float64').values
            df_2 = pd.read_csv(filename_3, delimiter=' ', header= None, index_col=False).astype('float64').values
#            ax2.plot(np.divide(df_2[:,0], df_2[:,2]), label = '{} nodes, Capture Effect={}, Inter-SF capture={}, pTX=[2, 5, 8, 11, 14]'.format(nrIntNodes, captureEffect, interSFInterference))
            if idx%2 == 0:
                ax2.plot(np.divide(df_2[:,0], df_2[:,2]), "--", label = '{} nodes, Capture Effect={}, Inter-SF capture={}, pTX=[14]'.format(nrIntNodes, captureEffect, interSFInterference))
            else:
                ax2.plot(np.divide(df_2[:,0], df_2[:,2]), label = '{} nodes, Capture Effect={}, Inter-SF capture={}, pTX=[2, 5, 8, 11, 14]'.format(nrIntNodes, captureEffect, interSFInterference))
            plt.xlabel("Horizon time (x100 hours)")
            plt.ylabel("Average energy using per successful transmitted packer per end-device [in J]")
            ax2.legend(loc='best')   
            plt.rcParams["font.family"] = "sans-serif"
            plt.rcParams["font.size"] = 12

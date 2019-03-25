#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 17:03:09 2019

@author: tuyenta
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from os.path import join
# args
nrNodes = int(100)
nrIntNodes = int(100)
nrBS = int(1)
initial = "RANDOM"
radius = float(4500)
avgSendTime = int(240000)
horTime = int(2e7)
packetLength = int(50)
sfSet = [7, 8, 9, 10, 11, 12]
freqSet = [868100] #[868100, 868300, 868500]
powSet = [14] #[2, 5, 8, 11, 14]
captureEffect_list = [True]
interSFInterference_list = [True]
info_mode = 'NO'

#make folder
exp_name = '100nodes_RANDOM' #'50nodes_5pows' # '50nodes_3channels' # '50nodes' '50nodes_5pows'
logdir = 'Sim_1'
simu_dir = join(logdir, exp_name)

for captureEffect in captureEffect_list:
    for interSFInterference in interSFInterference_list:
        fname = str(nrIntNodes) +'_smartNodes_' + 'initial_' +str(initial) + '_infoMode_' + str(info_mode) + '_captureEffect_' + str(captureEffect) + '_interSFMode_' + str(interSFInterference)

        setActions = [(sfSet[i], freqSet[j], powSet[k]) for i in range(len(sfSet)) for j in range(len(freqSet)) for k in range(len(powSet))]
        probDict = {}
        PacketReceptionRatio = {}

        # read and draw file
        marker_list = ["-", "-.", "--", "-s", "-x", "-o"]
        if nrIntNodes!=0:
            fig, ax = plt.subplots(figsize=(10, 4))
            setSF = [7, 8, 9, 10, 11, 12]
            setNodes = [0, 26, 89, 60, 29, 77]
            data = []
            for idx in range(len(setNodes)):
                nodeid = setNodes[idx]
                filename = join(simu_dir, str('prob_'+ fname) + '_id_' + str(nodeid) + '.csv')
                df = pd.read_csv(filename, delimiter=' ', header= None, index_col=False)
                df = df.replace(',', '', regex=True).astype('float64').values
                data.append(df[::200,idx])
            
            for idx in range(len(setNodes)):
                ax.plot(data[idx], marker_list[idx], label = 'id={}, SF = {}'.format(setNodes[idx], setSF[idx]))
                
                plt.xlabel("Horizon time (kHours)", fontsize=16)
                plt.ylabel("Probability", fontsize=16)
                    
                ax.legend(loc='upper center', bbox_to_anchor=(0, 1.05, 1, 0.2), ncol=3, fancybox=True, shadow=True)
                    
                plt.grid(True)
                plt.yticks(np.arange(0, 11)*0.1)
                plt.xticks(np.arange(0, 70, 10), ('0', '200', '400','600', '800', '1000', '1200'))
                plt.xlim(0, 40)
                plt.ylim(0,1.1)
                plt.rcParams["font.family"] = "sans-serif"
                plt.rcParams["font.size"] = 12  
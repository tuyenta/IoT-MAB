#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 14:05:43 2019

@author: tuyenta
"""
from lora.utils import print_params, sim

nrNodes = int(100)
nrIntNodes = int(100)
nrBS = int(1)
initial = "RANDOM"
radius = float(4500)
distribution = [0.1, 0.1, 0.3, 0.4, 0.05, 0.05]
avgSendTime = int(4*60*1000)
horTime = int(2e7)
packetLength = int(50)
sfSet = [7, 8, 9, 10, 11, 12]
freqSet = [868100]
powSet = [14]
captureEffect = True
interSFInterference = True
info_mode = 'NO'

# learning algorithm
algo = 'exp3'

# folder
exp_name = 'test_2'
logdir = 'Sim_2'


# print simulation parameters
print("\n=================================================")
print_params(nrNodes, nrIntNodes, nrBS, initial, radius, distribution, avgSendTime, horTime, packetLength, 
            sfSet, freqSet, powSet, captureEffect, interSFInterference, info_mode, algo)
assert initial in ["UNIFORM", "RANDOM"], "Initial mode must be UNIFORM, or RANDOM."
assert info_mode in ["NO", "PARTIAL", "FULL"], "Initial mode must be NO, PARTIAL, or FULL."
assert algo in ["exp3", "exp3s"], "Learning algorithm must be exp3 or exp3s."

# running simulation
bsDict, nodeDict = sim(nrNodes, nrIntNodes, nrBS, initial, radius, distribution, avgSendTime, 
                                horTime, packetLength, sfSet, freqSet, powSet, 
                                captureEffect, interSFInterference, info_mode, algo, logdir, exp_name)
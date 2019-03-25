#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 14:05:43 2019

@author: tuyenta
"""
from lora.utils import print_params, sim

nrNodes = int(1000)
nrIntNodes = int(1000)
nrBS = int(1)
initial = "RANDOM"
radius = float(4500)
avgSendTime = int(4*60*1000)
horTime = int(1e7)
packetLength = int(50)
sfSet = [7, 8, 9, 10, 11, 12]
freqSet = [868100]
powSet = [14]
captureEffect = True
interSFInterference = True
info_mode = 'NO'

#make folder
exp_name = 'test'
logdir = 'Sim_1'


# print simulation parameters
print("\n=================================================")
print_params(nrNodes, nrIntNodes, nrBS, initial, radius, avgSendTime, horTime, packetLength, 
            sfSet, freqSet, powSet, captureEffect, interSFInterference, info_mode)
assert initial in ["UNIFORM", "RANDOM"], "Initial mode must be UNIFORM, or RANDOM."
assert info_mode in ["NO", "PARTIAL", "FULL"], "Initial mode must be NO, PARTIAL, or FULL."
# running simulation
bsDict, nodeDict = sim(nrNodes, nrIntNodes, nrBS, initial, radius, avgSendTime, 
                                horTime, packetLength, sfSet, freqSet, powSet, 
                                captureEffect, interSFInterference, info_mode, logdir, exp_name)
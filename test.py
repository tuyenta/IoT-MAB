#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 14:05:43 2019

@author: tuyenta
"""
from lora.utils import print_params, sim

nrNodes = int(10)
nrIntNodes = int(10)
nrBS = int(1)
initial = "RANDOM"
radius = float(2000)
avgSendTime = int(360000)
horTime = int(100)
packetLength = int(50)
sfSet = [7, 8, 9, 10, 11, 12]
freqSet = [867300]
powSet = [14]
captureEffect = True
interSFInterference = True
info_mode = 'NO'

#make folder
exp_name = 'exp1'
logdir = 'logs'


# print simulation parameters
print("\n=================================================")
print_params(nrNodes, nrIntNodes, nrBS, initial, radius, avgSendTime, horTime, packetLength, 
            sfSet, freqSet, powSet, captureEffect, interSFInterference, info_mode)
assert initial in ["UNIFORM", "RANDOM"], "Initial mode must be UNIFORM, RANDOM."
# running simulation
bsDict, nodeDict = sim(nrNodes, nrIntNodes, nrBS, initial, radius, avgSendTime, 
                                horTime, packetLength, sfSet, freqSet, powSet, 
                                captureEffect, interSFInterference, info_mode, logdir, exp_name)
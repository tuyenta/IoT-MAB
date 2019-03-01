from lora.utils import print_params, sim

nrNodes = int(5)
nrIntNodes = int(5)
nrBS = int(1)
radius = float(2000)
avgSendTime = int(360000)
horTime = int(1e2)
packetLength = int(50)
sfSet = [7, 8]
freqSet = [867300]
powSet = [14]
captureEffect = True
interSFInterference = True
info_mode = 'NO'

#make folder
exp_name = 'exp3'
logdir = 'logs'


# print simulation parameters
print("\n=================================================")
print_params(nrNodes, nrIntNodes, nrBS, radius, avgSendTime, horTime, packetLength,
             sfSet, freqSet, powSet, captureEffect, interSFInterference, info_mode)

# running simulation
bsDict, nodeDict = sim(nrNodes, nrIntNodes, nrBS, radius, avgSendTime,
                       horTime, packetLength, sfSet, freqSet, powSet,
                       captureEffect, interSFInterference, info_mode, logdir, exp_name)

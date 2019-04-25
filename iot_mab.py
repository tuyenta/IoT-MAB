from lora.parse import get_args
from lora.utils import print_params, sim

def main(args):
    # import agruments
    nrNodes = int(args.nrNodes)
    nrIntNodes = int(args.nrIntNodes)
    nrBS = int(args.nrBS)
    initial = str(args.initial)
    radius = int(args.radius)
    distribution = list(map(float, args.distribution.split()))
    avgSendTime = int(args.AvgSendTime)
    horTime = int(args.horizonTime)
    packetLength = int(args.packetLength)
    sfSet = list(map(int, args.sfSet.split()))
    freqSet = list(map(int, args.freqSet.split()))
    powSet = list(map(int, args.powerSet.split()))
    captureEffect = bool(args.captureEffect)
    interSFInterference = bool(args.interSFInterference)
    info_mode = str(args.infoMode)
    algo = str(args.Algo)
    exp_name = str(args.exp_name)
    logdir = str(args.logdir)
    
    # print simulation parameters
    print("\n=================================================")
    print_params(nrNodes, nrIntNodes, nrBS, initial, radius, distribution, avgSendTime, horTime, packetLength, 
                sfSet, freqSet, powSet, captureEffect, interSFInterference, info_mode, algo)
    
    assert initial in ["UNIFORM", "RANDOM"], "Initial mode must be UNIFORM, RANDOM."
    assert info_mode in ["NO", "PARTIAL", "FULL"], "Initial mode must be NO, PARTIAL, or FULL."
    assert algo in ["exp3", "exp3s"], "Learning algorithm must be exp3 or exp3s."
    
    
    # running simulation
    bsDict, nodeDict = sim(nrNodes, nrIntNodes, nrBS, initial, radius, distribution, avgSendTime, horTime,
    packetLength, sfSet, freqSet, powSet, captureEffect, interSFInterference, info_mode, algo, logdir, exp_name)

    return bsDict, nodeDict

if __name__ == '__main__':
    # import agruments
    args = get_args()
    # print args and run simulation
    main(args)
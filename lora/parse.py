""" LPWAN Simulator: Hepper functions
============================================
Utilities (:mod:`lora.parse`)
============================================
.. autosummary::
   :toctree: generated/
   get_args                 -- Get the simulation's arguments
"""    
import argparse
#import argload

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nrNodes", required=True, type=int)
    parser.add_argument("--nrIntNodes", required=True, type=int)
    parser.add_argument("--nrBS", required=True, type=int, default=1)
    parser.add_argument("--initial", required=True, type=str)
    parser.add_argument("--radius", required=True, type=float, default=2)
    parser.add_argument("--distribution", required=True)
    parser.add_argument("--AvgSendTime", required=True, type=int, default=6)
    parser.add_argument("--horizonTime", required=True, type=int, default=10**6)
    parser.add_argument("--packetLength", required=True, type=int, default=50)
    parser.add_argument("--freqSet", required=True, default='867100')
    parser.add_argument("--sfSet", required=True, default='7 8 9 10 11 12')
    parser.add_argument("--powerSet", required=True, default=14)
    parser.add_argument("--captureEffect", required=True, type=int)
    parser.add_argument("--interSFInterference", required=True, type=int)
    parser.add_argument("--infoMode", required=True, type=str)
    parser.add_argument("--Algo", required=True, type=str)
    parser.add_argument("--logdir", required=True, type=str)
    parser.add_argument("--exp_name", required=True, type=str)
    
#     parser = argload.ArgumentLoader(
#         parser, to_reload=['nrNodes', 'nrIntNodes', 'nrBS', 'radius', 'AvgSendTime', 'horizonTime',
#          'packetLength', 'freqSet', 'sfSet', 'powerSet', 'captureEffect' 'interSFInterference', 'infoMode',
#          'logDir'])
    return parser.parse_args()

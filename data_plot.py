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
captureEffect_list = [True, False]
interSFInterference_list = [True, False]
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
            for nodeid in [0]: #[26, 89, 60, 29, 77]:    
                filename = join(simu_dir, str('prob_'+ fname) + '_id_' + str(nodeid) + '.csv')
                df = pd.read_csv(filename, delimiter=' ', header= None, index_col=False)
                df = df.replace(',', '', regex=True).astype('float64').values

                fig, ax = plt.subplots(figsize=(10, 4))
                for idx in range(df.shape[1]):
                    if setActions[idx][0] in [7, 8, 9, 10, 11, 12]:
                        ax.plot(df[::200,idx], marker_list[idx%6], label = 'SF = {}, freq={}'.format(setActions[idx][0], setActions[idx][1]))
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
                    #plt.close(fig)
                # save to file
                fig.savefig(join(simu_dir, str(fname) + '_id_' + str(nodeid) + '.png'))
                # probDict
                probDict[nodeid] = df[-1 , :]
                
            # save probDict and packet reception ratio     
            np.save(join(simu_dir, str('prob_'+ fname)), probDict)
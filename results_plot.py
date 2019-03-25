import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from os.path import join

# args
nrNodes = int(100)
nrIntNodes_list = [0, 0, 50, 50, 100]
nrBS = int(1)
initial_list = ["RANDOM", "UNIFORM"]
radius = float(4500)
avgSendTime = int(240000)
horTime = int(1e7)
packetLength = int(50)
sfSet = [7, 8, 9, 10, 11, 12]
freqSet = [868100, 868300, 868500]
powSet = [14] #[2, 5, 8, 11, 14]
captureEffect_list = [False]
interSFInterference_list = [True, False]
info_mode = 'NO'

#make folder
exp_name_list = ['0node_UNIFORM_3channels', '0node_RANDOM_3channels', '50nodes_UNIFORM_3channels', '50nodes_RANDOM_3channels', '100nodes_UNIFORM_3channels']
#exp_name_list = ['0node_RANDOM', '50nodes_RANDOM', '100nodes_RANDOM']

logdir = 'Sim_1'
fig1, ax1 = plt.subplots(figsize=(12,5))
#fig2, ax2 = plt.subplots(figsize=(12,8))
#fig3, ax3 = plt.subplots(figsize=(12,10))

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
            
            #initial = "RANDOM"      
            fname = str(nrIntNodes) +'_smartNodes_' + 'initial_' +str(initial) + '_infoMode_' + str(info_mode) + '_captureEffect_' + str(captureEffect) + '_interSFMode_' + str(interSFInterference)
            filename_1 = join(simu_dir, str('ratio_'+ fname) + '.csv')
            filename_2 = join(simu_dir, str('traffic_'+ fname) + '.csv')
            filename_3 = join(simu_dir, str('energy_'+ fname) + '.csv')
            df_1 = pd.read_csv(filename_1, delimiter=' ', header= None, index_col=False).astype('float64').values
            df_2 = pd.read_csv(filename_2, delimiter=' ', header= None, index_col=False).astype('float64').values
            df_3 = pd.read_csv(filename_3, delimiter=' ', header= None, index_col=False).astype('float64').values
            marker_list_1 = ["--", "-.", ":", "-", "-x"]
            marker_list_2 = ["+", "*", "o", "s", "d"]
#           
            if nrIntNodes == 100:
                if interSFInterference == True:
                    ax1.plot(df_2[::200,1], marker_list_1[idx], markersize=8, linewidth=2.0, label = '{}%, Inter-SF'.format(nrIntNodes))
                else:
                    ax1.plot(df_2[::200,1], marker_list_2[idx], markersize=8, linewidth=2.0, label = '{}%, w/o Inter-SF'.format(nrIntNodes))
            else:
                if interSFInterference == True:
                    ax1.plot(df_2[::200,1], marker_list_1[idx], markersize=8, linewidth=2.0, label = '{}%, {}, Inter-SF'.format(nrIntNodes, initial))
                else:
                    ax1.plot(df_2[::200,1], marker_list_2[idx], markersize=8, linewidth=2.0, label = '{}%, {}, w/o Inter-SF'.format(nrIntNodes, initial))
            
            
            plt.xlabel("Horizon time (kHours)", fontsize=16)
            plt.ylabel("(Average) Normalized Total Throughput", fontsize=16)
            plt.yticks(np.arange(2, 7)*0.1)
            plt.xlim([0, 10])
            plt.xticks(np.arange(0, 60, 10),('0', '200', '400','600', '800', '1000', '1200'))
            ax1.legend(loc='upper center', bbox_to_anchor=(0, 1.15, 1, 0.2), ncol=3, fancybox=True, shadow=True)
            plt.grid(True)
            plt.rcParams["font.family"] = "sans-serif"
            plt.rcParams["font.size"] = 12
#            
#            if interSFInterference == True:
#                ax2.plot(df_2[::200,1], marker_list_1[idx], label = '{}%, InterSF'.format(nrIntNodes))
#            else:
#                ax2.plot(df_2[::200,1], marker_list_2[idx], label = '{}%, w/o InterSF'.format(nrIntNodes))
#            plt.xlabel("Horizon time (kHours)", fontsize=16)
#            plt.ylabel("(Average) Normalized Total Throughput", fontsize=16)
#            ax2.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=3, fancybox=True, shadow=True)  
#            plt.grid(True)
#            plt.yticks(np.arange(2, 4.2, 0.2)*0.1)
#            plt.xticks(np.arange(0, 40, 10),('0', '200', '400', '600', '800'))
#            plt.rcParams["font.family"] = "sans-serif"
#            plt.rcParams["font.size"] = 13
#            
#            ax3.plot(df_2[:,1], label = '{} nodes, Capture Effect={}, Inter-SF capture={}'.format(nrIntNodes, captureEffect, interSFInterference))
#            plt.xlabel("Horizon time (x1000)")
#            plt.ylabel("(Average) Throughput")
#            ax3.legend(loc='best')   
#            plt.rcParams["font.family"] = "sans-serif"
#            plt.rcParams["font.size"] = 12
#            plt.close(fig)
#        # save to file
#    fig.savefig(join(simu_dir, str(fname) + '_id_' + str(nodeid) + '.png'))
""" LPWAN Simulator: Hepper functions
============================================
Utilities (:mod:`lora.bsFunctions`)
============================================
.. autosummary::
   :toctree: generated/
   transmitPacket           -- Transmission process with discret event simulation.
   cuckooClock              -- Notify the simulation time (for each 1k hours).
   saveProb                 -- Save the probability profile of each node.
"""    
import os
import random
from os.path import join
from .loratools import airtime
# Transmit
def transmitPacket(env, node, bsDict, logDistParams):
    """ Transmit a packet from node to all BSs in the list.
    Parameters
    ----------
    env : simpy environement
        Simulation environment.
    node: my Node
        LoRa node.
    bsDict: dict
        list of BSs.
    logDistParams: list
        channel params
    Returns
    -------
    """
    while True:
        # The inter-packet waiting time. Assumed to be exponential here.
        yield env.timeout(random.expovariate(1/float(node.period)))
        
        # update settings if any
        node.updateTXSettings()
        node.resetACK()
        node.packetNumber += 1
        
        # send a virtual packet to each base-station in range and those we may affect
        for bsid, dist in node.proximateBS.items():
            prob_temp = [node.prob[x] for x in node.prob]
            node.packets[bsid].updateTXSettings(bsDict, logDistParams, prob_temp)
            bsDict[bsid].addPacket(node.nodeid, node.packets[bsid])
            bsDict[bsid].resetACK()
        
        #print("Start transmitting packet at t= {}".format(int(1+env.now/(6*60*1000))) + " from node {}".format(node.nodeid))
        #print(node.prob)
        #print(node.weight)
        #for pkid in bsDict[bsid].packets.keys():    
        #    print(pkid, bsDict[bsid].packets[pkid].sf, bsDict[bsid].packets[pkid].freq, bsDict[bsid].packets[pkid].pTX)                   
        
        # wait until critical section starts
        Tcritical = (2**node.packets[0].sf/node.packets[0].bw)*(node.packets[0].preambleLength - 5) # time until the start of the critical section
        yield env.timeout(Tcritical)
        
        # make the packet critical on all nearby basestations
        for bsid in node.proximateBS.keys():
            bsDict[bsid].makeCritical(node.nodeid)
            
        Trest = airtime((node.packets[0].sf, node.packets[0].rdd, node.packets[0].bw, node.packets[0].packetLength, node.packets[0].preambleLength, node.packets[0].syncLength, node.packets[0].headerEnable, node.packets[0].crc)) - Tcritical # time until the rest of the message completes
        yield env.timeout(Trest)
        
        successfulRx = False
        ACKrest = 0
        
        # transmit ACK
        for bsid in node.proximateBS.keys():
            #print("=====> eval bs {}".format(bsid))
            if bsDict[bsid].removePacket(node.nodeid):
                bsDict[bsid].addACK(node.nodeid, node.packets[bsid])
                ACKrest = airtime((node.packets[0].sf, node.packets[0].rdd, node.packets[0].bw, node.packets[0].packetLength, node.packets[0].preambleLength, node.packets[0].syncLength, node.packets[0].headerEnable, node.packets[0].crc))# time until the ACK completes
                yield env.timeout(ACKrest)
                node.addACK(bsDict[bsid].bsid, node.packets[bsid])
                successfulRx = True
                
        # update probability        
        node.packetsTransmitted += 1
        if successfulRx:
            if node.info_mode in ["NO", "PARTIAL"]:
                node.packetsSuccessful += 1
                node.transmitTime += node.packets[0].rectime
            elif node.info_mode == "FULL": 
                if not node.ack[0].isCollision:
                    node.packetsSuccessful += 1
                    node.transmitTime += node.packets[0].rectime
            node.updateProb()
        #print("Probability of action from node " +str(node.nodeid)+ " at (t+1)= {}".format(int(1+env.now/(6*60*1000))))
        #print(node.prob)
        #print(node.weight)
        # wait to next period
        yield env.timeout(float(node.period)-Tcritical-Trest-ACKrest)
        #input()
def cuckooClock(env):
    """ Notifies the simulation time.
    Parameters
    ----------
    env : simpy environement
        Simulation environment.
    Returns
    -------
    """
    while True:
        yield env.timeout(1e3 * 3600000)
        print("Running {} kHrs".format(env.now/(1e3 * 3600000)))

def saveProb(env, nodeDict, fname, simu_dir):
    """ Save probabilities every 1e1 hours
    Parameters
    ----------
    env : simpy environement
        Simulation environment.
    nodeDict:dict
        list of nodes.
    fname: string
        file name structure
    simu_dir: string
        folder
    Returns
    -------
    """
    while True:
        yield env.timeout(1e3 * 360000)
        # write prob to file
        for nodeid in nodeDict.keys():
             if nodeDict[nodeid].node_mode == "SMART":
                filename = join(simu_dir, str('prob_'+ fname) + '_id_' + str(nodeid) + '.csv')
                save = str(list(nodeDict[nodeid].prob.values()))[1:-1]
                if os.path.isfile(filename):
                    res = "\n" + save
                else:
                    res = save
                with open(filename, "a") as myfile:
                    myfile.write(res)
                myfile.close()

        # write packet reception ratio to file
        nTransmitted = 0
        nRecvd = 0
        PacketReceptionRatio = 0
        for nodeid in nodeDict.keys():
            nTransmitted += nodeDict[nodeid].packetsTransmitted
            nRecvd += nodeDict[nodeid].packetsSuccessful
        PacketReceptionRatio = nRecvd/nTransmitted
        filename = join(simu_dir, str('ratio_'+ fname) + '.csv')
        if os.path.isfile(filename):
            res = "\n" + str(PacketReceptionRatio)
        else:
            res = str(PacketReceptionRatio)
        with open(filename, "a") as myfile:
            myfile.write(res)
        myfile.close()
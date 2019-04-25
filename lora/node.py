from __future__ import division
import numpy as np
from .loratools import getDistanceFromPower
from .packet import myPacket

class myNode():
    """ LPWAN Simulator: node
    Base station class
   
    |category /LoRa
    |keywords lora
    
    \param [IN] nodeid: id of the node
    \param [IN] position: position of the node in format [x y]
    \param [IN] transmitParams: physical layer's parameters
    \param [IN] bsList: list of BS
    \param [IN] interferenceThreshold: interference threshold
    \param [IN] logDistParams: log shadowing channel parameters
    \param [IN] sensi: sensitivity matrix
    \param [IN] nSF: number of spreading factors
    
    """
    def __init__(self, nodeid, position, transmitParams, initial, sfSet, freqSet, powSet, bsList,
                 interferenceThreshold, logDistParams, sensi, node_mode, info_mode, horTime, algo, simu_dir, fname):
        self.nodeid = nodeid # id
        self.x, self.y = position # location
        if node_mode == 0:
            self.node_mode = initial
        else:
            self.node_mode = "SMART"
        
        self.info_mode = info_mode # 'no', 'partial', 'full'
        
        self.bw = int(transmitParams[2])
        self.period = float(transmitParams[9])
        self.pTXmax = max(powSet) # max pTX
        self.sensi = sensi
        
        # generate proximateBS
        self.proximateBS = self.generateProximateBS(bsList, interferenceThreshold, logDistParams)
    
        # set of actions
        self.freqSet = freqSet
        self.powerSet = powSet

        if self.info_mode == "NO":     
            self.sfSet = sfSet
        else:
            self.sfSet = self.generateHoppingSfFromDistance(sfSet, logDistParams)
        
        self.setActions = [(self.sfSet[i], self.freqSet[j], self.powerSet[k]) for i in range(len(self.sfSet)) for j in range(len(self.freqSet)) for k in range(len(self.powerSet))]
        self.nrActions = len(self.setActions)
        self.initial = initial
        
        # learning algorithm
        if algo == 'exp3':
            self.learning_rate = np.minimum(1, np.sqrt((self.nrActions*np.log(self.nrActions))/((horTime)*(np.exp(1.0)-1))))
            self.alpha = None
        elif algo == 'exp3s':
            self.learning_rate = np.minimum(1, np.sqrt((self.nrActions*np.log(self.nrActions*horTime))/horTime))
            self.alpha = 1/horTime 
        # weight and prob for learning
        self.weight = {x: 1 for x in range(0, self.nrActions)}
        if self.initial=="RANDOM":
            prob = np.random.rand(self.nrActions)
            prob = prob/sum(prob)   
        else:
            prob = (1/self.nrActions) * np.ones(self.nrActions)      
        self.prob = {x: prob[x] for x in range(0, self.nrActions)}

        # generate packet and ack
        self.packets = self.generatePacketsToBS(transmitParams, logDistParams)
        self.ack = {}
        
        # measurement params
        self.packetNumber = 0
        self.packetsTransmitted = 0
        self.packetsSuccessful = 0
        self.transmitTime = 0
        self.energy = 0
    def generateProximateBS(self, bsList, interferenceThreshold, logDistParams):
        """ Generate dictionary of base-stations in proximity.
        Parameters
        ----------
        bsList : list
            list of BSs.
        interferenceThreshold: float
            Interference threshold
        logDistParams: list
            Channel parameters
        Returns
        -------
        proximateBS: list
            List of proximated BS
        """

        maxInterferenceDist = getDistanceFromPower(self.pTXmax, interferenceThreshold, logDistParams)
        dist = np.sqrt((bsList[:,1] - self.x)**2 + (bsList[:,2] - self.y)**2)
        index = np.nonzero(dist <= maxInterferenceDist)

        proximateBS = {} # create empty dictionary
        for i in index[0]:
            proximateBS[int(bsList[i,0])] = dist[i]

        return proximateBS
    
    def generatePacketsToBS(self, transmitParams, logDistParams):
        """ Generate dictionary of base-stations in proximity.
        Parameters
        ----------
        transmitParams : list
            Transmission parameters.
        logDistParams: list
            Channel parameters
        Returns
        -------
        packets: packet
            packets at BS
        """
        packets = {} # empty dictionary to store packets originating at a node
        
        for bsid, dist in self.proximateBS.items():
            packets[bsid] = myPacket(self.nodeid, bsid, dist, transmitParams, logDistParams, self.sensi, self.setActions, self.nrActions, self.sfSet, self.prob) #choosenAction)
        return packets
    #print("probability of node " +str(self.nodeid)+" is: " +str(self.prob))

    def generateHoppingSfFromDistance(self, sfSet, logDistParams):
        """ Generate the sf hopping sequence from distance
        Parameters
        ----------
        logDistParams: list in format [gamma, Lpld0, d0]
            Parameters for log shadowing channel model.
        Returns
        -------
    
        """
        sfBuckets = []
        gamma, Lpld0, d0 = logDistParams
        dist = self.proximateBS[0]
        
        if self.bw == 125:
            bwInd = 0
        else:
            bwInd = 1
        Lpl = self.pTXmax - self.sensi[:, bwInd+1]
        
        LplMatrix = Lpl.reshape((6,1))
        distMatrix =np.dot(d0, np.power(10, np.divide(LplMatrix - Lpld0, 10*gamma)))
        
        for i in range(6):
            if dist <= distMatrix[0, 0]:
                minSF = 7
            elif distMatrix[i, 0 ]<= dist < distMatrix[i+1, 0]:
                minSF = (i + 1) + 7
        tempSF = [sf for sf in sfSet if sf >= minSF]
        sfBuckets.extend(tempSF)
        
        return sfBuckets
    
    def updateProb(self, algo):
        """ Update the probability of each action by using EXP3 algorithm.
        Parameters
        ----------
       
        Returns
        -------
    
        """
        prob = [self.prob[x] for x in self.prob]
        weight = [self.weight[x] for x in self.weight]
        reward = np.zeros(self.nrActions)
        # compute reward
        if self.node_mode == "SMART":
            # no and partial information case:
            if self.info_mode in ["NO", "PARTIAL"]:
                # with ACK -> 1, no ACK -> 0
                    if self.ack:
                        reward[self.packets[0].choosenAction] = 1/prob[self.packets[0].choosenAction]
                    else:
                        reward[self.packets[0].choosenAction] = 0
            # full information case:
            else:
                if self.ack:
                    if not self.ack[0].isCollision:
                        reward[self.packets[0].choosenAction] = 1/prob[self.packets[0].choosenAction]
                    else:
                        reward[self.packets[0].choosenAction] = 0.5/prob[self.packets[0].choosenAction]
                else:
                    reward[self.packets[0].choosenAction] = 0
        
        # update weight
        for j in range(0, self.nrActions):
            if algo == "exp3":
                weight[j] *= np.exp((self.learning_rate * reward[j])/self.nrActions)
            elif algo == "exp3s":
                weight[j] *= np.exp((self.learning_rate * reward[j])/self.nrActions)
                weight[j] += ((np.exp(1) * self.alpha)/self.nrActions) * sum(weight)
        
        # update prob
        if self.node_mode == "SMART":
            for j in range(0, self.nrActions):
                prob[j] = (1-self.learning_rate) * (weight[j]/sum(weight)) + (self.learning_rate/self.nrActions)
        elif self.node_mode == "RANDOM":
            prob = np.random.rand(self.nrActions)
            prob = prob/sum(prob)
        else:
            prob = (1/self.nrActions) * np.ones(self.nrActions)
        
        # trick: force the small value (<1/5000) to 0 and normalize
        prob = np.array(prob)
        prob[prob<0.0005] = 0
        prob = prob/sum(prob)
        self.weight = {x: weight[x] for x in range(0, self.nrActions)} 
        self.prob = {x: prob[x] for x in range(0, self.nrActions)}
        
    def resetACK(self):
        """Reset ACK"""
        self.ack = {}
        
    def addACK(self, bsid, packet):
        """Send an ACK to the node"""
        self.ack[bsid] = packet 
    
    def updateTXSettings(self):
        """Update TX setting"""
        pass
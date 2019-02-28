from numpy import zeros, random, where
from .loratools import getRXPower, dBmTomW, airtime

class myPacket():
    """ LPWAN Simulator: packet
    Base station class
   
    |category /LoRa
    |keywords lora
    
    \param [IN] nodeid: id of the node
    \param [IN] bsid: id of the base station
    \param [IN] dist: distance between node and bs
    \param [IN] transmitParams: physical layer parameters
                [sf, rdd, bw, packetLength, preambleLength, syncLength, headerEnable, crc, pTX, period] 
    \param [IN] logDistParams: log shadowing channel parameters
    \param [IN] sensi: sensitivity matrix
    \param [IN] setActions: set of possible actions
    \param [IN] nrActions: number of actions
    \param [IN] sfSet: set of spreading factors
    \param [IN] prob: probability
    """

    def __init__(self, nodeid, bsid, dist, transmitParams, logDistParams, sensi, setActions, nrActions, sfSet, prob): #choosenAction):
        self.nodeid = nodeid
        self.bsid = bsid
        self.dist = dist
        
        # params
        self.sf = int(transmitParams[0])
        self.rdd = int(transmitParams[1])
        self.bw = int(transmitParams[2])
        self.packetLength = int(transmitParams[3])
        self.preambleLength = int(transmitParams[4])
        self.syncLength = transmitParams[5]
        self.headerEnable = int(transmitParams[6])
        self.crc = int(transmitParams[7])
        self.pTXmax = int(transmitParams[8])
        self.sensi = sensi
        self.sfSet = sfSet
        
        # learn strategy
        self.setActions = setActions
        self.nrActions = nrActions
        self.prob = [prob[x] for x in prob]
        #self.choosenAction = choosenAction
        #self.sf, self.freq, self.pTX = self.setActions[self.choosenAction]
        self.sf = None
        self.freq= None
        self.pTX = self.pTXmax
        
        #received params
        self.rectime = airtime(transmitParams[0:8])
        self.pRX = getRXPower(self.pTX, self.dist, logDistParams)
        self.signalLevel = None

        # measurement params
        self.packetNumber = 0
        self.isLost = False
        self.isCritical = False
        self.isCollision = False
                
    def computePowerDist(self, bsDict, logDistParams):
        """ Get the power distribution .
        Parameters
        ----------
        self : packet
            Packet.
        bsDict: dictionary
            Dictionary of BSs
        Returns
        -------
        signalLevel: dictionary
            The power contribution of a packet in various frequency buckets for each BS
    
        """
        signal = self.getPowerContribution()
        signalLevel = {x:signal[x] for x in signal.keys() & bsDict[self.bsid].signalLevel.keys()}
        return signalLevel
        
    def updateTXSettings(self, bsDict, logDistParams, prob):
        """ Update the TX settings after frequency hopping.
        Parameters
        ----------
        bsDict: dictionary
            Dictionary of BSs
        logDistParams: list
            Channel parameters, e.x., log-shadowing model: (gamma, Lpld0, d0)]
        
        Returns
        isLost: bool
            Packet is lost ot not by compare the pRX with RSSI
        -------
    
        """
        self.packetNumber += 1
        self.prob = prob
        self.choosenAction = random.choice(self.nrActions, p=self.prob)
        self.sf, self.freq, self.pTX = self.setActions[self.choosenAction]
        self.pRX = getRXPower(self.pTX, self.dist, logDistParams)
        #print("probability of node " +str(self.nodeid)+" is: " +str(self.prob))

        self.signalLevel = self.computePowerDist(bsDict, logDistParams)

        if self.pRX >= self.sensi[self.sf-7, 1+int(self.bw/250)]:
            self.isLost = False
        else:
            self.isLost = True
            #print(self.pRX)
            #print ("Node " + str(self.nodeid) + ": packet is lost (smaller than RSSI)!")
   
        self.isCritical = False
        
    def getAffectedFreqBuckets(self):
        """ Get the list of affected frequency buckets from [fc-bw/2 fc+bw/2].
        Parameters
        ----------
        
        Returns
        fRange: list
            List of frequencies that effected by the using frequency
        -------
        """
        low = self.freq - self.bw/2 # Note: this is approx due to integer division for 125
        high = self.freq + self.bw/2 # Note: this is approx due to integer division for 125
        lowBucketStart = int(low - (low % 200) + 100)
        highBucketEnd = int(high + 200 - (high % 200) - 100)

        # the +1 ensures that the last value is included in the set
        return range(lowBucketStart, highBucketEnd + 1, 200)
            
    def getPowerContribution(self):
        """ Get the power contribution of a packet in various frequency buckets.
        Parameters
        ----------

        Returns
        powDict: dic
            Power distribution by frequency
        -------
    
        """
        freqBuckets = self.getAffectedFreqBuckets()
        powermW = dBmTomW(self.pRX)
        #print(self.pRX, powermW)
        signal = zeros((6,1))
        full_setSF = [7, 8, 9, 10, 11, 12]
        idx = full_setSF.index(self.sf)
        #print(idx)
        signal[idx] = powermW
        #print(signal)
        return {freqBuckets[0]:signal}
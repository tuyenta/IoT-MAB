import numpy as np
from .loratools import dBmTomW
class myBS():
    """ LPWAN Simulator: base station
    Base station class
   
    |category /LoRa
    |keywords lora
    
    \param [IN] bsid: id of the base station
    \param [IN] position: position of the base station in format [x y]
    \param [IN] isRouge: 
    \param [IN] interactionMatrix: interaction matrix for a pair of SF
    \param [IN] nDemodulator: number of demodulators for each BS
    
    """
    
    """ init the lora bs parameters"""
    def __init__(self, bsid, position, interactionMatrix, nDemodulator, ackLength, freqSet, sfSet, captureThreshold):
        self.bsid = bsid
        self.x, self.y = position
        self.nDemodulator = nDemodulator
        self.ackLength = ackLength
        self.interactionMatrix = interactionMatrix
        self.captureThreshold = captureThreshold
        
        # packet and ack
        self.packets = {}
        self.ack = {}
        self.packetsInBucket = {}
        self.signalLevel = {}

        self.sfSet = sfSet
        for freq in freqSet:
            self.packetsInBucket[freq] = {}
            self.signalLevel[freq] = np.zeros((6,1))
        
        # measurement params
        self.demodulator = set()
        self.successNo = 0
    
    def addPacket(self, nodeid, packet):
        """ Send a packet to the base station.
        Parameters
        ----------
        nodeid: int
            ID of the node
        packet: packet
            packet from node
        Returns
        packets: list of packet
            List of packets at BS.
        -------
        """
        for fbucket in packet.signalLevel.keys():
            #print("before-" + str(self.signalLevel[fbucket]))
            self.signalLevel[fbucket] = self.signalLevel[fbucket] + packet.signalLevel[fbucket]
            #print("after-" + str(self.signalLevel[fbucket]))
            self.evaluateFreqBucket(fbucket)
            self.packetsInBucket[fbucket][nodeid] = packet
        self.packets[nodeid] = packet
    
    def resetACK(self):
        self.ack = {}
        
    def addACK(self, nodeid, packet):
        """ Send an ACK to the node.
        Parameters
        ----------
        nodeid: int
            ID of the node
        packet: packet
            packet from node
        Returns
        ack: packet
            ACK from BS.
        -------
        """
        for fbucket in packet.signalLevel.keys():
            self.evaluateFreqBucket(fbucket)
            self.successNo += 1
        self.ack[self.successNo] = packet

            
    def evaluateFreqBucket(self, fbucket):
        """ Packet from node enters critical section.
        Parameters
        ----------
        fbucket: list
            List of frequency buckets
        
        Returns
        isLost: bools
            Packet is lost or not.
        -------
        """
        signalInBucket = np.dot(self.interactionMatrix, self.signalLevel[fbucket])
        for nodeid, pkt in self.packetsInBucket[fbucket].items():
            if not pkt.isLost and pkt.isCritical:
                if self.captureThreshold != 0:
                    if (1 + self.captureThreshold)*(pkt.signalLevel[fbucket][pkt.sf - 7]) < self.captureThreshold * self.signalLevel[fbucket][pkt.sf - 7]:
                        pkt.isLost = True # CE
                    else:
                        if (1 + self.captureThreshold)*(pkt.signalLevel[fbucket][pkt.sf - 7]) < signalInBucket[pkt.sf - 7]:
                            pkt.isLost = True # InterSF
                        else:
                            if (pkt.signalLevel[fbucket][pkt.sf - 7]) < self.signalLevel[fbucket][pkt.sf - 7]:
                                pkt.isCollision = True # collision
                else:
                    if pkt.signalLevel[fbucket][pkt.sf - 7] < self.signalLevel[fbucket][pkt.sf - 7]:
                        pkt.isLost = True # collision
                        pkt.isCollision = True # collision
                    else:
                        if pkt.signalLevel[fbucket][pkt.sf - 7] < signalInBucket[pkt.sf - 7]:
                            pkt.isLost = True # interSF

    def makeCritical(self, nodeid):
        """ Packet from node enters critical section.
        Parameters
        ----------
        nodeid: int
            ID of the node
        
        Returns
        [isLost, isCollision, isCritical]: list of bools
            Packet is lost and/or collision and/or critical or not.
        -------
        """
        pkt = self.packets[nodeid]
        if not pkt.isLost:
            if self.evaluatePacket(nodeid)[0] and len(self.demodulator) <= self.nDemodulator and (pkt.freq, pkt.bw, pkt.sf) not in self.demodulator:
                self.demodulator.add((pkt.freq, pkt.bw, pkt.sf))
                pkt.isCritical = True
                if self.evaluatePacket(nodeid)[1]:
                    pkt.isCollision = False
                else:
                    pkt.isCollision = True
            else:
                pkt.isLost = True
                pkt.isCritical = False
                
    def evaluatePacket(self, nodeid):
        """ Evaluate packet by consider the capture effect and inter-SF interference conditions.
        Parameters
        ----------
        nodeid: int
            ID of the node
        
        Returns
        [lostFlag, (not) collisionFlag]: list of bools
            Packet is lost and/or collision or not.
        -------
        """
        pkt = self.packets[nodeid]
        if pkt.isLost:
            return False
        else:
            lostFlag = False
            collisionFlag = False
            for fbucket in pkt.signalLevel.keys():
                # print("Receiver power from node "+str(nodeid)+" is "+ str(pkt.signalLevel[fbucket][pkt.sf - 7]))
                # print("Total power at bs is " + str(self.signalLevel[fbucket][pkt.sf - 7]))
                signalInBucket = np.dot(self.interactionMatrix[pkt.sf - 7].reshape(1,6), self.signalLevel[fbucket])
                # print("Total power of signal in Frequency is " + str(signalInBucket))
                # packet is lost of not due to capture effect and interSF collision
                
                # with Capture Effect
                if self.captureThreshold !=0:
                    # Capture effect
                    if (1 + self.captureThreshold)*(pkt.signalLevel[fbucket][pkt.sf - 7]) < self.captureThreshold * self.signalLevel[fbucket][pkt.sf - 7]:
                        lostFlag = True
                        collisionFlag = True
                        # print ("Packet from node "+ str(nodeid) +" is lost due to Capture effect!")  
                    else:
                        # interSF collision
                        if (1 + self.captureThreshold)*(pkt.signalLevel[fbucket][pkt.sf - 7]) < signalInBucket:
                            lostFlag = True
                            # print ("Packet from node "+ str(nodeid) +" is lost due to InterSF collision!") 
                        else:
                            # packet received but collied
                            if (pkt.signalLevel[fbucket][pkt.sf - 7]) < self.signalLevel[fbucket][pkt.sf - 7]:
                                collisionFlag = True
                                # print ("Packet from node "+ str(nodeid) +" is received but collied!")
                
                # without Capture effect
                else:
                    # packet is collision or not
                    if pkt.signalLevel[fbucket][pkt.sf - 7] < self.signalLevel[fbucket][pkt.sf - 7]:
                        lostFlag = True
                        collisionFlag = True
                        # print ("Packet from node "+ str(nodeid) +" is lost due to collision (w/o Capture Effect)")  
                    else:
                        # interSF collision
                        if pkt.signalLevel[fbucket][pkt.sf - 7] < signalInBucket:
                            lostFlag = True
                            # print ("Packet from node "+ str(nodeid) +" is lost due to InterSF collision (w/o Capture Effect)!") 
            return [not lostFlag, not collisionFlag]

    def removePacket(self, nodeid):
        """ Stop sending a packet to the base station i.e. Remove it from all relevant lists.
        Parameters
        ----------
        nodeid: int
            ID of the node
        
        Returns
        removePacket: bool
            Packet is critical and is not lost.
        -------
        """
        pkt = self.packets[nodeid]
        # if packet was being demodulated, free the demodulator
        if pkt.isCritical and (pkt.freq, pkt.bw, pkt.sf) in self.demodulator:
            # only successfully demodulated packets i.e. Those that are critical are considered to be received
            self.demodulator.remove((pkt.freq, pkt.bw, pkt.sf))
        for fbucket in pkt.signalLevel.keys():
            self.signalLevel[fbucket] = self.signalLevel[fbucket] - pkt.signalLevel[fbucket]
            # rounding problem - float 64
            self.signalLevel[fbucket][self.signalLevel[fbucket]< 1e-27] = 0
            foo = self.packetsInBucket[fbucket].pop(nodeid)
        foo = self.packets.pop(nodeid)
        return pkt.isCritical and not pkt.isLost
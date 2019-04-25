""" LPWAN Simulator: Hepper functions
============================================
Utilities (:mod:`lorawan.loratools`)
============================================
.. autosummary::
   :toctree: generated/
   dec2bin                  -- Integer to binary (bit array) with a fixed width.
   dec2bin_matrix           -- Interfer to binary (bit matrix): [xmin xmax].
   bitarray2dec             -- Binary (bit array) to integer.
   hamming_dist             -- Hamming distance.
   euclid_dist              -- Squared Euclidean distance.
   upsample                 -- Upsample by an integral factor (zero insertion).
   dBmTomW                  -- dBm to mW
   dBmTonW                  -- dBm to nW
   getRXPower               -- Get RX power
   getTXPower               -- Get TX power
   getDistanceFromPL        -- Get distance from power lost
   getDistanceFromPower     -- Get distance from TX and RX powers
   getFreqBucketsFromSet    -- Get frequencies set
   placeRandomly            -- Place a node (bs) randomly
   placeRandomlyInRange     -- Place randomly nodes in a range
   getMaxTransmitDistance   -- Get maximum transmit distance (for US)
   
With some codes from CommPy library: http://veeresht.github.com/CommPy
and LoRaSim library: https://github.com/adwaitnd/lorasim

"""    

# Import Library
import numpy as np
import math
import random
__all__ = ['dec2bitarray', 'bitarray2dec', 'dec2bitmatrix', 'hamming_dist', 'euclid_dist', 'upsample','dBmTomW', 'dBmTonW', 'getRXPower', 'getTXPower', 'getDistanceFromPL', 'getDistanceFromPower', 'getFreqBucketsFromSet', 'airtime', 'getMaxTransmitDistance']

def dec2bitarray(in_number, bit_width):
    """
    Converts a positive integer to NumPy array of the specified size containing
    bits (0 and 1).
    Parameters
    ----------
    in_number : int
        Positive integer to be converted to a bit array.
    bit_width : int
        Size of the output bit array.
    Returns
    -------
    bitarray : 1D ndarray of ints
        Array containing the binary representation of the input decimal.
    """
    k = bin(in_number)[2:].zfill(bit_width)
    bin_array = [int(i) for i in k]
    return(bin_array)

def bitarray2dec(in_bitarray):
    """
    Converts an input NumPy array of bits (0 and 1) to a decimal integer.
    Parameters
    ----------
    in_bitarray : 1D ndarray of ints
        Input NumPy array of bits.
    Returns
    -------
    number : int
        Integer representation of input bit array.
    """

    number = 0

    for i in range(len(in_bitarray)):
        number = number + in_bitarray[i]*pow(2, len(in_bitarray)-1-i)

    return number

def dec2bitmatrix(xmin, xmax):
    """
    Converts a range of positive integer from minimum to maximum value to NumPy
    array of the specified size containing bits (0 and 1).
    Parameters
    ----------
    min_number : int
        Minimum positive integer to be converted to a bit array.
    max_number : int
        Maximum positive integer to be converted to a bit array.
    Returns
    -------
    bitmatrix : 2D ndarray of ints
        Matrix containing the binary representation of the input decimal.
    """
    width = np.floor(np.log2(xmax)+1)
    distance = xmax - xmin
    bitmatrix = np.zeros((int(distance)+1, int(width)))
    for i in range(int(distance+1)):
        bitmatrix[i,:] = dec2bitarray(xmin+i, int(width))
    return(bitmatrix)    

def hamming_dist(in_bitarray_1, in_bitarray_2):
    """
    Computes the Hamming distance between two NumPy arrays of bits (0 and 1).
    Parameters
    ----------
    in_bit_array_1 : 1D ndarray of ints
        NumPy array of bits.
    in_bit_array_2 : 1D ndarray of ints
        NumPy array of bits.
    Returns
    -------
    distance : int
        Hamming distance between input bit arrays.
    """

    distance = np.bitwise_xor(in_bitarray_1, in_bitarray_2).sum()

    return distance

def euclid_dist(in_array1, in_array2):
    """
    Computes the squared euclidean distance between two NumPy arrays
    Parameters
    ----------
    in_array1 : 1D ndarray of floats
        NumPy array of real values.
    in_array2 : 1D ndarray of floats
        NumPy array of real values.
    Returns
    -------
    distance : float
        Squared Euclidean distance between two input arrays.
    """
    distance = ((in_array1 - in_array2)*(in_array1 - in_array2)).sum()

    return distance

def upsample(x, n):
    """
    Upsample the input array by a factor of n
    Adds n-1 zeros between consecutive samples of x
    Parameters
    ----------
    x : 1D ndarray
        Input array.
    n : int
        Upsampling factor
    Returns
    -------
    y : 1D ndarray
        Output upsampled array.
    """
    y = np.empty(len(x)*n, dtype=complex)
    y[0::n] = x
    zero_array = np.zeros(len(x), dtype=complex)
    for i in range(1, n):
        y[i::n] = zero_array

    return y
""" The log-distance model
    Lpl = Lpld0 + 10*gamma*log10(d/d0) + X_normal
    model paramaters are initialized to NaNs to ensure they're setup befor being used
"""

def dBmTomW(pdBm):
    """
    dBm to mW converter
    Parameters
    ----------
    pdBm : float
        Power in dBm.
    Returns
    -------
    pmW : float (>0)
        Power in mW.
	"""
    pmW = 10.0**(pdBm/10.0)
    return pmW

def dBmTonW(pdBm):
	"""
    dBm to nW converter
    Parameters
    ----------
    pdBm : float
        Power in dBm.
    Returns
    -------
    pmW : float (>0)
        Power in nW.
	"""
	pnW = 10.0**((pdBm+90.0)/10.0)
	return pnW

def getRXPower(pTX, distance, logDistParams):
    """
    Get ideal RX power estimate assuming log-distance model.
    Parameters
    ----------
    pTX : float
        Power in dBm.
    distance: float
        Distance in m
    logDistParams: list in format [gamma, Lpld0, d0]
        Parameters for log shadowing channel model.
    Returns
    -------
    pRX : float (>0)
        Receiver signal power.
    """
    gamma, Lpld0, d0 = logDistParams
    pRX = pTX - Lpld0 - 10.0*gamma*np.log10(distance/d0)
    return pRX
	
def getTXPower(pRX, distance, logDistParams):
    """
    Get ideal TX power estimate assuming log-distance model.
    Parameters
    ----------
    pRx : float
        Power in dBm.
    distance: float
        Distance in m
    logDistParams: list in format [gamma, Lpld0, d0]
        Parameters for log shadowing channel model.
    Returns
    -------
    pmW : float (>0)
        Transmitter signal power.
    """
    gamma, Lpld0, d0 = logDistParams
    pTX = pRX + Lpld0 + 10.0*gamma*np.log10(distance/d0)
    return pTX

def getDistanceFromPL(pLoss, logDistParams):
    """
    Get distance from the power loss.
    Parameters
    ----------
    pLoss : float
        Power loss in dB.
    logDistParams: list in format [gamma, Lpld0, d0]
        Parameters for log shadowing channel model.
    Returns
    -------
    d : float (>0)
        Distance in m.
    """
    gamma, Lpld0, d0 = logDistParams
    d = d0*(10.0**((pLoss-Lpld0)/(10.0*gamma)))
    return d

def getDistanceFromPower(pTX, pRX, logDistParams):
	"""
    Get distance from the transmission and reception powers.
    Parameters
    ----------
    pTX : float
        Transmisison power.
    pRx: float
        Reception power.
    logDistParams: list in format [gamma, Lpld0, d0]
        Parameters for log shadowing channel model.
    Returns
    -------
    d : float (>0)
        Distance in m.
	"""
	return getDistanceFromPL(pTX - pRX, logDistParams)

def getFreqBucketsFromSet(nbChannels):
    """
    Get the list of frequencies for various bandwidths used by our base-stations.
    This is currently only applicable to the Euroupe specifications.
    Parameters
    ----------
    BSFreqSetList : farrayloat
        Set of freq list.
    Returns
    -------
    freqBuckets : set
        Set of frequencies
	"""
    minfreq = 867100
    maxfreq = 868500
    freqBuckets = []
    freqBuckets.extend(np.linspace(minfreq, maxfreq, nbChannels, dtype=int))
    return freqBuckets

def placeRandomly(number, locArray, xRange, yRange):
    """ Place location of a node (or bs) randomly
    Parameters
    ----------
    number : int
        Number of nodes (or BSs).
    xRange: [xmin xmax]
        Range of a node in x-axis.
    yRange: [ymin ymax]
        Range of a node in y-axis.
    Returns
    -------
    locArray: array
        Location array.
    """
    for n in range(number):
        x = random.uniform(xRange[0], xRange[1])
        y = random.uniform(yRange[0], yRange[1])
        locArray[n,:] = [n, x, y]
        

def placeRandomlyInRange(number, nrIntNodes, locArray, xRange, yRange, refLoc, bestValue,
                         radius, transmitParams, maxPtx, distribution, distMatrix):
    """ Place node randomly in a range
    Parameters
    ----------
    number : int
        Number of nodes (or BSs).
    nrIntNodes: int
        Number of intelligent nodes
    xRange: [xmin xmax]
        Range of a node in x-axis.
    yRange: [ymin ymax]
        Range of a node in y-axis.
    refLoc: array
        Location of a BS
    bestValue: list
        Best Dist, bestSF, bestBW from a node to BS 
    radius: float
        Radius of simulation
    transmitParams: list
        Transmission params
    maxPtx: float
        Maximum transmission value
    distribution: list
        Distribution of nodes
    distMatrix: matrix
        Matrix of distance sperated by SF and BW
    Returns
    -------
    locArray: array
        Location array.
    """
    temp = 0
    for idx in range(len(distribution)):
        number_nodes = int(number * distribution[idx])
        for n in range(number_nodes):
            while True:
                # This could technically turn into an infinite loop but that shouldn't ever practically happen.
                # add check here later
                x = random.uniform(xRange[0], xRange[1])
                y = random.uniform(yRange[0], yRange[1])
                #print(x, y)
                rdd, packetLength, preambleLength, syncLength, headerEnable, crc = transmitParams
                bestDist, bestSF, bestBW = bestValue
                if idx == 0:
                    if np.any(np.sum(np.square(refLoc[:,1:3] - np.array([x,y]).reshape(1,2)), axis=1) <= radius**2):
                        if np.any(np.sum(np.square(refLoc[:,1:3] - np.array([x,y]).reshape(1,2)), axis=1) <= distMatrix[idx]**2):
                            locArray[n+temp,:] = [n+temp, x, y, bestSF, rdd, bestBW, packetLength, preambleLength, syncLength, headerEnable, crc, maxPtx, 0, 0]
                            break
                else:
                    if np.any(np.sum(np.square(refLoc[:,1:3] - np.array([x,y]).reshape(1,2)), axis=1) <= radius**2):
                        if np.any(np.sum(np.square(refLoc[:,1:3] - np.array([x,y]).reshape(1,2)), axis=1) <= distMatrix[idx]**2):
                            if np.any(np.sum(np.square(refLoc[:,1:3] - np.array([x,y]).reshape(1,2)), axis=1) >= distMatrix[idx-1]**2):
                                locArray[n+temp,:] = [n+temp, x, y, bestSF, rdd, bestBW, packetLength, preambleLength, syncLength, headerEnable, crc, maxPtx, 0, 0]
                                break
        temp += number_nodes

def airtime(phyParams):
    """ Computes the airtime of a packet in second.
    Parameters
    ----------
    sf : int [7...12]
        Spreading factor.
    rdd: int [1 2 3 4]
        coding rate of Hamming code.
    bw: int [125kHz 250kHz 5000 kHz]
        bandwidth.
    packetlen: int
        lenght of the packet.
    preamble_len: int
        legth of the preamble.
    sync_len: int
        length of the sync words.
    hearder_enable: boolean
        enable hearder.
    crc: boolean
        enable crc or not
    Returns
    -------
    Tpream + Tpayload: float
        The time on air of a packer in second.
    """
    DE = 1       # low data rate optimization enabled (=1) or not (=0)
    sf, rdd, bw, packetLength, preabmleLength, syncLength, headerEnable, crc = phyParams
#    if bw == 125 and sf in [11, 12]:
#        # low data rate optimization mandated for BW125 with SF11 and SF12
#        DE = 1
#    if sf == 6:
#        # can only have implicit header with SF6
#        headerEnable = True

    Tsym = (2.0**sf)/bw
    Tpream = (preabmleLength + syncLength)*Tsym
    payloadSymbNB = 8 + max(math.ceil((8.0*packetLength-4.0*sf+28+16*crc-20*headerEnable)/(4.0*(sf-2*DE)))*(rdd+4),0)
    Tpayload = payloadSymbNB * Tsym
    return Tpream + Tpayload

def getMaxTransmitDistance(RXSensi, maxPtx, logDistParams, phyParams):
    """ Get the best range for for allowed power from the the transmit time and bandwidth used.
    This is dependent on the packet length as the max transmission size is also limited.
    Only for EU.
    Parameters
    ----------
    RXSensi : int
        Number of nodes (or BSs).
    maxPtx: float
        Maximum power of transmission
    logDistParams: list in format [gamma, Lpld0, d0]
        Parameters for log shadowing channel model.
    phyParams: list in format [rdd, packetlen, hearder_enable, preabmle_len, crc]
        Parameters for the packet.
    Returns
    -------
    distMatrix: float
        Maximum distance value.
    maxSF: int [7...12]
        Maximum spreading factor to get the max distance.
    maxBW: int [125 250] kHz
        Maximum bandwidth to get the max distance.

    """
    
    gamma, Lpld0, d0 = logDistParams
    rdd, packetLength, headerEnable, preambleLength, syncLength, crc = phyParams
   
    PTx125 = min(maxPtx,14) # in dBm
    PTx250 = min(maxPtx,14) # in dBm
   
    Lpl125 = PTx125 - RXSensi[:,1]
    Lpl250 = PTx250 - RXSensi[:,2]
    
    
    LplMatrix = np.concatenate((Lpl125.reshape((6,1)), Lpl250.reshape((6,1))), axis=1)
    distMatrix =np.dot(d0, np.power(10, np.divide(LplMatrix - Lpld0, 10*gamma)))
    
    packetAirtimeValid = np.zeros((6,2))
    for i in range(6):
        # set packet airtime valid <= 400
        packetAirtimeValid[i,0] = (airtime((i+7, rdd, 125, packetLength, preambleLength, syncLength, headerEnable, crc)) <= 9999)
        packetAirtimeValid[i,1] = (airtime((i+7, rdd, 250, packetLength, preambleLength, syncLength, headerEnable, crc)) <= 9999)
    Index = np.argmax(np.multiply(distMatrix, packetAirtimeValid))
    
    sfInd, bwInd = np.unravel_index(Index, (6,2))
    if packetAirtimeValid[sfInd, bwInd] == 0:
        raise ValueError("Packet length too large!")
    
    maxSF = sfInd + 7
    if bwInd == 0:
        maxBW = 125
    else:
        maxBW = 250
    
    return distMatrix[:, bwInd], distMatrix[sfInd,bwInd], maxSF, maxBW
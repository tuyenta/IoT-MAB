""" LPWAN Simulator: Foward Error Correction Code
============================================
Utilities (:mod:`lora.fec`)
============================================
.. autosummary::
   :toctree: generated/   
   hamming              -- hamming code.
       + encode              
       + decode
   
"""

# Import Library
from numpy import append, arange, concatenate, c_, dot, zeros, ones
from numpy import array, identity, mod, power, matmul  
from loratools import dec2bitmatrix

class hamming:
    """ LPWAN Simulator: Hamming Code Generator    
    Generate the Hamming code through the code generator matrix G
    and the parity-check matrix H
    Parity bit:
        x1 x2 x3 x4 p1 (4/5)
        x1 x2 x3 x4 p1 p2 (4/6)
        x1 x2 x3 x4 p1 p2 p3 (4/7)
        x1 x2 x3 x4 p1 p2 p3 p4 (4/8)
    Error detection: 4/5, 4/6, 4/7, 4/8    
    Error correction: 4/7. 4/8
    
    |category /LoRa
    |keywords lora
        
    \param [IN] cr: the coding rate
   
    \param [OUT] G: the code generator matrix
    \param [OUT] H: the parity check matrix 
    
    """    
    # init the lora modulation parameters
    def __init__(self, rdd):
        self.rdd = rdd
        # Hamming code generator
        # G: code generator matrix
        # H: parity-check matrix        
        if self.rdd == 1:
            # case 1: simple parity check
            P = ones((4,1))
            self.G = c_[identity(4),P]
            self.H = append(P, 1).transpose()            
            self.syndrom_check = [0, 1]            
        elif self.rdd == 2:
            # case 2: shortened Hamming
            temp = dec2bitmatrix(0, 7)
            P = temp[temp.sum(axis=1)>=2]
            P = P[:,[1, 2]]
            self.G = c_[identity(4),P]
            self.H = concatenate((P, identity(3)))
        elif self.rdd == 3:
            # case 3: Hamming(7,4)
            temp = dec2bitmatrix(0, 7)
            P = temp[temp.sum(axis=1)>=2]
            self.G = c_[identity(4),P]
            self.H = concatenate((P, identity(3)))
        elif self.rdd == 4:
            # case 4: Extended Hamming(8,4)           
            temp = dec2bitmatrix(0, 7)
            P = temp[temp.sum(axis=1)>=2]
            P = c_[P,array(mod(1+P.sum(axis=1),2)).T]
            self.G = c_[identity(4),P]
            self.H = concatenate((P, identity(4)))
        # Coset leader LUT            
        self.cl = zeros((2**self.rdd, 4 + rdd))
        self.cl_found = zeros(2**self.rdd-1)
        for i in range(self.rdd + 4):
            syn = int(matmul((array(self.H[i,:])), array(power(2, arange(self.rdd -1, -1, -1))).T))-1
            
            if not(self.cl_found[syn]):
                self.cl[syn, i] = 1
                self.cl_found[syn] = 1
            else:
                self.cl_found[syn] = 2       
        
        if any(x==0 for x in self.cl_found):
            for i1 in range(4 + self.rdd-1):
                for i2 in range(i1, 4+self.rdd):
                    syn = int(matmul(mod(self.H[i1,:]+self.H[i2,:],2),array(power(2, arange(self.rdd-1,-1,-1))).T))-1                    
                    if not(self.cl_found[syn]):
                        self.cl[syn,[i1,i2]]=1
                        self.cl_found[syn]=1
                    else:
                        self.cl_found[syn]=2
        
    # Encode
    def encode(self, input_message):
        enc = dot(input_message,self.G)%2
        return enc
    
    # Parity check and correct error and decode the message
    def decode(self,received_message):
        temp = list(received_message)
        if self.rdd >2:
            syn = int(matmul(dot(received_message,self.H)%2,array(power(2, arange(self.rdd-1,-1,-1))).T))-1            
            if (syn!=-1) and (self.cl_found[syn]==1):       
                temp = mod(temp+self.cl[syn,:],2)
                error = False 
            else:
                error = True
            bit_est = temp[0:4]      
        return(error, bit_est)

""" LPWAN Simulator: Convolution Code Generator    
    Generate the convolution code through the code generator matrix G
    and the parity-check matrix H
    |category /LoRa
    
    |keywords lora
    Parity bit:
        x1 x2 x3 x4 p1 (4/5)
        x1 x2 x3 x4 p1 p2 (4/6)
        x1 x2 x3 x4 p1 p2 p3 (4/7)
        x1 x2 x3 x4 p1 p2 p3 p4 (4/8)
    Error detection: 4/5, 4/6, 4/7, 4/8    
    Error correction: 4/7. 4/8
    
    \param [IN] cr: the coding rate
   
    \param [OUT] G: the code generator matrix
    \param [OUT] H: the parity check matrix
    
    """
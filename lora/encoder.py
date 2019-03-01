""" LPWAN Simulator: Encoding
============================================
Utilities (:mod:`lorawan.encoder`)
============================================
.. autosummary::
   :toctree: generated/   
   grayIndexing         -- Gray indexing.
   interleaving         -- Interleaving.
   errorEncoding        -- FEC coding.

"""

# Import Library
from .fec import hamming
from .loratools import dec2bitmatrix
from numpy import size, dot, zeros, mod, c_, power, append 

# Define the LoRa Modulation class
class LoRaEncode:
    """ LPWAN Simulator: Lora Decoding
    Decode the demodulated symbols into the bits stream
    Process: bits -> whitening -> header + CRC -> error coding -> interleaving -> (inverse) gray mapping -> symbols
    
    |category /LoRa
    |keywords lora
    
    \param [IN] sf: spreading factor of the chirp spreading spectrum
    \param [IN] cr: coding rate cr=["4/5" "4/6" "4/7" "4/8"]
    \param [IN] explicit: enable explicit explicit =[True False]
    \param [IN] crc: enable crc crc=[True False]
    \param [IN] whitening: enable whitening whitening= [True False]
    \param [IN] the demodulated symbols
    
    \param [OUT] the coded message     
    
     """
    def __init__(self, sf, cr, explicit, crc, whitening):
        # check
        assert type(sf) is int, "Spreading factor must be an interger."
        assert (sf>=7) and (sf<=12), "Spreading factor must be in 7 to 12."
        assert (cr=="4/4") or (cr == "4/5") or (cr == "4/6") or (cr == "4/7") or (cr == "4/8"), "Invalid coding rate."
        assert type(explicit) is bool, "Explicit must be a boolean [True for On, False for Off]."
        assert type(crc) is bool, "CRC must be a boolean [True for On, False for Off]."
        assert type(whitening) is bool, "Whitening must be a boolean [True for On, False for off]."
        # init the lora modulation parameters
        self.sf = sf        
        if   (cr == "4/5"): self.rdd = 1
        elif (cr == "4/6"): self.rdd = 2
        elif (cr == "4/7"): self.rdd = 3
        elif (cr == "4/8"): self.rdd = 4
        self.explicit=explicit
        self.crc=crc
        self.whitening=whitening
    
    """ setting the default values"""
    def reactive(self):
        self.sf = 10
        self.rdd = 1
        self.explicit=True
        self.crc=True
        self.whitening=False
   
    """ set spreading factor"""
    def setSpreadFactor(self, sf):
        self.sf = sf
        return(self)
    
    """ set coding rate """
    def setCodingRate(self, cr):
       assert (cr == "4/5") or (cr == "4/6") or (cr == "4/7") or (cr == "4/8"), "Invalid coding rate."
       if   (cr == "4/5"): self.rdd = 1
       elif (cr == "4/6"): self.rdd = 2
       elif (cr == "4/7"): self.rdd = 3
       elif (cr == "4/8"): self.rdd = 4
       return(self)
   
    """ set whitening actor"""
    def enableWhitening(self, whitening):
       assert type(whitening) is bool, "Whitening must be a boolean [True for On, False for Off]."
       self.whitening = whitening
       return(self)
  
    """ set explicit factor"""
    def enableExplicit(self, explicit):
       assert type(explicit) is bool, "Explicit must be a boolean [True for On, False for Off]."
       self.explicit = explicit
       return(self)
   
    """ set crc factor"""
    def enableCrc(self, crc):
       assert type(crc) is bool, "Explicit must be a boolean [True for On, False for Off]."
       self.crc = crc
       return(self)
        
   # whitenning process
   #def whitening(self, bits):
   #    if self.whitening==True:
   #        whiten_seq = 
   #return(whitened)
    """=================== Encoding ==================="""
    def errorEncoding(self,bits):
        """ Forward Error Correction.
        Parameters
        ----------
        bits : list
            Input message
        Returns
        -------
        code_words: list
            Codeds message
        """ 
        hamming_code = hamming(self.rdd)       
        global N_bits 
        global N_codewords
        global N_codebits
        global N_syms
        global N_blocks
        global interleaver_size
        global sym_len
        N_bits = size(bits)
        N_codewords = N_bits/4
        N_codebits =  N_codewords * (self.rdd+ 4)
        N_syms = N_codebits/self.sf
        interleaver_size = (4+self.rdd)*self.sf
        N_blocks = N_codebits/interleaver_size
        """ for debug """
        # print(N_bits, N_codewords, N_codebits, N_syms, interleaver_size, N_blocks)
        
        code_words = zeros((int(N_codewords), 4 + self.rdd))
        for i in range(int(N_codewords)):
            code_words[i, :] = hamming_code.encode(bits[i * 4 : (i+1) * 4])
        return(code_words)
   
    def interleaving(self, codewords):
        """ Interleaving.
        Parameters
        ----------
        codewords : list
            Coded message
        Returns
        -------
        gray_coded: list
            Interleaved message
        """      
        interleaved = zeros((int(N_syms),int(self.sf)))
        for i in range(int(N_blocks)):
            for k in range(int(4+self.rdd)):
                for m in range(int(self.sf)):
                    interleaved[(4+self.rdd)*i+k,m] = codewords[self.sf*i+(m-k)%self.sf,k]                    
        return(interleaved)
    
    def grayIndexing(self, interleaved):
        """ Gray indexing.
        Parameters
        ----------
        interleaved : list
            Interleaved message
        Returns
        -------
        gray_coded: list
            Gray coded message
        """          
        # gray mapping LUT
        dec2bin = dec2bitmatrix(0, 2**self.sf-1) # dec2bin lookup table                       
        bin2dec = power(2, range(self.sf-1, -1, -1)).transpose()
        g= dot(mod(dec2bin+c_[zeros(2**self.sf),dec2bin[:,:-1]], 2), bin2dec) # gray
        ig= zeros(2**self.sf) # inverse gray
        for i in range(2**self.sf): 
            ig[int(g[i])] = i
        # gray indexing
        k = zeros(int(N_syms))
        """ for debug """
        #gray_indexed = zeros((int(N_syms),int(self.sf)))
        
        for sym in range(int(N_syms)):
            k[sym]= ig[int(dot(interleaved[sym,:],bin2dec))]            
            #gray_indexed[sym, :] = dec2bin[int(k[sym]),:]          
        
        return(k)
    
    """=================== Decoding ==================="""
    
    def grayDecoding(self, demod):
        """ De-Gray indexing.
        Parameters
        ----------
        demod : list
            Demodulated message
        Returns
        -------
        gray_decoded: list
            Gray decoded message
        """          
        
        # for debug
        #print(N_syms, N_codebits, N_codewords, N_bits, N_blocks)
        
        # gray mapping LUT
        dec2bin = dec2bitmatrix(0, 2**self.sf-1) # dec2bin lookup table                       
        bin2dec = power(2, range(self.sf-1, -1, -1)).transpose()
        g= dot(mod(dec2bin+c_[zeros(2**self.sf),dec2bin[:,:-1]], 2), bin2dec) # gray
        ig= zeros(2**self.sf) # inverse gray
        for i in range(2**self.sf): 
            ig[int(g[i])] = i
        # gray indexing
        gray_decoded = zeros((int(N_syms),int(self.sf)))       
        for sym in range(int(N_syms)):
            gray_decoded[sym, :] = dec2bin[int(g[int(demod[sym])]),:]          
        return(gray_decoded)        
    
    def deInterleaving(self, gray_decoded): 
        """ De-interleaving.
        Parameters
        ----------
        gray_decoded : list
            Interleaved message
        Returns
        -------
        interleaved: bool
            Deinterleaved message
        """       
        interleaved = zeros((int(N_codewords), 4 + self.rdd))
        for i in range(int(N_blocks)):
            for k in range(int(4+self.rdd)):
                for m in range(int(self.sf)):
                    interleaved[self.sf*i +(m-k)%self.sf, k] = gray_decoded[(4+self.rdd)*i+k, m]                    
        return(interleaved)

    def errorDecoding(self,interleaved):
        """ Forward Error Correction Decoding: """
        """ Forward Error Correction Decoding.
        Parameters
        ----------
        interleaved : list
            interleaved signal
        Returns
        -------
        error: bool
            Result of fec check (True of False)
        decoded: list
            Decoded message
        """      
        hamming_code = hamming(self.rdd) 
        """ For debug """
        #print(interleaved)
        
        decoded = []
        error = []
        for i in range(int(N_codewords)):
            temp_1, temp_2 = hamming_code.decode(interleaved[i,:])
            error = append(error, temp_1)           
            decoded = append(decoded, temp_2)
        return(error, decoded)                 
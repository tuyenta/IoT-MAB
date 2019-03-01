""" LPWAN Simulator: Hepper functions
============================================
Utilities (:mod:`lorawan.modulation`)
============================================
.. autosummary::
   :toctree: generated/
   CSSMod               -- chirp spread spectrum modulation.
   FSK                  -- frequecy shift keying modulation.
   PSKModem             -- Phase Shift Keying (PSK) Modem.
   QAMModem             -- Quadrature Amplitude Modulation (QAM) Modem.
   mimo_ml              -- MIMO Maximum Likelihood (ML) Detection.
"""
__all__ = ['ChirpMod', 'PSKModem', 'QAMModem', 'mimo_ml']

# Import Library
from numpy import arange, array, zeros, pi, cos, sin, sqrt, log2, argmin, \
                  hstack, repeat, tile, dot, sum, shape, concatenate, exp, \
                  log, vectorize, power, size, append, complex_, argmax
from itertools import product
from .loratools import bitarray2dec, dec2bitarray
from numpy.fft import fft, ifft

# Define the chirp generator class
class genChirp:
    """ Generate a chirp
    \param [IN] sf: spreading factor of the chirp spreading spectrum
    \param [IN] bw: bandwidth of the CSS modulation
    \param [IN] fs: sampling frequency
    \param [IN] Nsamples: number of samples
    \param [IN] up/downchirp factor [True: Upchirp False: downchirp]
    \param [IN] phase0: initial phase for modulation    
    \param [IN] symbol: input symbol of chirp modulation
    \param [OUT] the chirp 
    """
    # init the lora modulation parameters
    def __init__(self, sf, bw, fs, mu, phase0):
        # check
        assert type(sf) is int, "Spreading factor must be an interger."
        assert (sf>=7) and (sf<=12), "Spreading factor must be in 7 to 12."
        assert type(mu) is bool, "Upchirp/Downchirp factor must be a boolean [True for Up, False for Down]."
        # init the lora modulation parameters
        self.sf = sf
        self.bw = bw
        self.fs = fs
        self.Nsamples = self.fs*power(2,self.sf)/self.bw       
        self.mu = mu        
        self.phase0 = phase0

    # generate the chirp signal
    def genChirpSig(self, symbol):
        """ Generate chirp signal.
        Parameters
        ----------
        symbol : int
            Input of chirp generator
        Returns
        -------
        out_preamble: 1D array of complext floats
            CSS chirp
        """   
        # intitialization
        phase = self.phase0        
        freq_offset = (self.fs/2)-(self.bw/2)
        shift = symbol
        out_preamble = zeros(int(self.Nsamples), dtype='complex_')
        
        for k in range(int(self.Nsamples)):
            # output the complex signal
            out_preamble[k] = cos(phase) + 1j * sin(phase)
            
            # frequency from cyclic shift
            f = self.bw * shift/(power(2,self.sf))
            if self.mu==False:
                f = self.bw - f
            
            # apply Frequency offset away from DC
            f = f + freq_offset
    
            # Increase the phase according to frequency
            phase = phase + 2*pi*f/self.fs
            if phase > pi:
                phase = phase - 2*pi
    
            # update cyclic shift
            shift = shift + self.bw/self.fs
            if shift >= power(2, self.sf): 
                shift = shift - power(2, self.sf)
        return(out_preamble)

class ChirpMod:
    """ LPWAN Simulator: Lora Mod
    Modulate LoRa packets from symbols into a complex sample stream.
    |category /LoRa
    |keywords lora
    \param [IN] sf: spreading factor of the chirp spreading spectrum
    \param [IN] bw: bandwidth of the CSS modulation
    \param [IN] fs: sampling frequency
    \param [IN] Nsamples: number of samples
    \param [IN] up/downchirp factor [True: Upchirp False: downchirp]
    \param [IN] phase0: initial phase for modulation    
    \param [IN] preabmle_len: the length of preamble
    \param [IN] sync_len: the length of sync
    \param [IN] message: the coded message
    \param [OUT] the modulated message    
    """    
    # init the lora modulation parameters
    def __init__(self, sf, bw, fs, mu, phase0):
        # check
        assert type(sf) is int, "Spreading factor must be an interger."
        assert (sf>=7) and (sf<=12), "Spreading factor must be in 7 to 12."
        assert type(mu) is bool, "Upchirp/Downchirp factor must be a boolean [True for Up, False for Down]."
        # init the lora modulation parameters
        self.sf = sf
        self.bw = bw
        self.fs = fs
        self.Nsamples = self.fs*power(2,self.sf)/self.bw 
        self.mu = mu        
        self.phase0 = phase0
    
    # setting the default values
    def reactive(self):
        self.sf = 10
        self.bw = 125000
        self.fs = 10**6
        self.Nsamples = self.fs*power(2,self.sf)/self.bw       
        self.mu = True        
        self.phase0 = 0

    # chirp spread spectrum modulation
    def CSSMod(self, preamble_len, sync_len, message):
        """ CSS Modulation.
        Parameters
        ----------
        preamble_len : int
            Length of preamble
        sync_len : int
            Length of sync
        message: 1D array of floats
            Transmitted message at transmitter
        Returns
        -------
        out_message: 1D array of floats
            CSS modulated signal
        """    
        # init the modulated message       
        out_message = []        
        # Preamble Generation
        mod_preamble = []
        preamble_symb = 0        
        for k in range(preamble_len):            
            mod_preamble = genChirp.genChirpSig(self,preamble_symb)
            out_message = append(out_message, mod_preamble)
        """ for debug """
        # print(self.Nsamples)
        # Sync Generation
        mod_sync = []
        sync_symbol = 32
        for k in range(sync_len):
            self.mu = False
            mod_sync = genChirp.genChirpSig( self, sync_symbol)
            out_message = append(out_message, mod_sync)            
        # Symbol Generation
        mod_message = []
        for k in range(size(message)):
            self.mu = True
            mod_message = genChirp.genChirpSig(self, message[k])
            out_message = append(out_message, mod_message)            
        return(out_message)
    
    # chirp spread spectrum demodulation
    def CSSDemod(self, preamble_len, sync_len, total_len, received_message):
        """ CSS Demodulation.
        Parameters
        ----------
        preamble_len : int
            Length of preamble
        sync_len : int
            Length of sync
        total_len: int
            Total length of message
        received_message: 1D array of floats
            Received message at receiver
        Returns
        -------
        demod_message: 1D array of floats
            CSS demodulated signal
        """       
        demod_message = zeros(int(total_len - preamble_len - sync_len))
        
        # generate the reverse chirp
        self.mu = False
        reverse_symbol = 0
        reverse_chirp = genChirp.genChirpSig( self, reverse_symbol)        
        
        # multiply the received message with the recerse chirp
        demod_out = zeros(int(total_len) * int(self.Nsamples), dtype=complex_)
        for n in range(int(total_len)):
            demod_out[n * int(self.Nsamples) : (n+1) * int(self.Nsamples)] = array(received_message[n * int(self.Nsamples) : (n+1) * int(self.Nsamples)]) * array(reverse_chirp)
        
        # computing FFT
        fft_out = zeros((int(total_len), int(self.Nsamples)))
        for m in range(int(total_len)):            
            fft_out[m,:] = abs(fft(demod_out[m * int(self.Nsamples) : (m+1) * int(self.Nsamples)]))
            #print(np.size(np.fft.fft(demod_out[m * int(self.Nsamples) : (m+1) * int(self.Nsamples)])))
        # demodulates the received data
        k = 0
        """ - the maximum point can <= Nsamples/2 or > Nsamples/2, however, we take the smaller one
        """
        for m in range(preamble_len+sync_len,total_len):
            #print(np.argmax(fft_out[m,:]))
            if argmax(fft_out[m,:]) < (2**self.sf):
                demod_message[k] = argmax(fft_out[m,:])
            else:
                demod_message[k] = argmax(fft_out[m,:(2**self.sf)])
            k = k+1
        
        return(demod_message)   
# for other modulation methods
class Modem:
    def modulate(self, input_bits):
        """ Modulate (map) an array of bits to constellation symbols.
        Parameters
        ----------
        input_bits : 1D ndarray of ints
            Inputs bits to be modulated (mapped).
        Returns
        -------
        baseband_symbols : 1D ndarray of complex floats
            Modulated complex symbols.
        """
        mapfunc = vectorize(lambda i:
            self.constellation[bitarray2dec(input_bits[i:i+self.num_bits_symbol])])

        baseband_symbols = mapfunc(arange(0, len(input_bits), self.num_bits_symbol))

        return baseband_symbols

    def demodulate(self, input_symbols, demod_type, noise_var = 0):
        """ Demodulate (map) a set of constellation symbols to corresponding bits.
        Supports hard-decision demodulation only.
        Parameters
        ----------
        input_symbols : 1D ndarray of complex floats
            Input symbols to be demodulated.
        demod_type : string
            'hard' for hard decision output (bits)
            'soft' for soft decision output (LLRs)
        noise_var : float
            AWGN variance. Needs to be specified only if demod_type is 'soft'
        Returns
        -------
        demod_bits : 1D ndarray of ints
            Corresponding demodulated bits.
        """
        if demod_type == 'hard':
            index_list = map(lambda i: argmin(abs(input_symbols[i] - self.constellation)), \
                             range(0, len(input_symbols)))
            demod_bits = hstack(map(lambda i: dec2bitarray(i, self.num_bits_symbol),
                                index_list))
        elif demod_type == 'soft':
            demod_bits = zeros(len(input_symbols) * self.num_bits_symbol)
            for i in arange(len(input_symbols)):
                current_symbol = input_symbols[i]
                for bit_index in arange(self.num_bits_symbol):
                    llr_num = 0
                    llr_den = 0
                    for const_index in self.symbol_mapping:
                        if (const_index >> bit_index) & 1:
                            llr_num = llr_num + exp((-abs(current_symbol - self.constellation[const_index])**2)/noise_var)
                        else:
                            llr_den = llr_den + exp((-abs(current_symbol - self.constellation[const_index])**2)/noise_var)
                    demod_bits[i*self.num_bits_symbol + self.num_bits_symbol - 1 - bit_index] = log(llr_num/llr_den)
        else:
            pass
            # throw an error

        return demod_bits
# PSK Modulation
class PSKModem(Modem):
    """ Creates a Phase Shift Keying (PSK) Modem object. """

    def _constellation_symbol(self, i):
        return cos(2*pi*(i-1)/self.m) + sin(2*pi*(i-1)/self.m)*(0+1j)

    def __init__(self, m):
        """ Creates a Phase Shift Keying (PSK) Modem object.
        Parameters
        ----------
        m : int
            Size of the PSK constellation.
        """
        self.m = m
        self.num_bits_symbol = int(log2(self.m))
        self.symbol_mapping = arange(self.m)
        self.constellation = list(map(self._constellation_symbol,
                                 self.symbol_mapping))
# QAM Modulation
class QAMModem(Modem):
    """ Creates a Quadrature Amplitude Modulation (QAM) Modem object."""

    def _constellation_symbol(self, i):
        return (2*i[0]-1) + (2*i[1]-1)*(1j)

    def __init__(self, m):
        """ Creates a Quadrature Amplitude Modulation (QAM) Modem object.
        Parameters
        ----------
        m : int
            Size of the QAM constellation.
        """

        self.m = m
        self.num_bits_symbol = int(log2(self.m))
        self.symbol_mapping = arange(self.m)
        mapping_array = arange(1, sqrt(self.m)+1) - (sqrt(self.m)/2)
        self.constellation = list(map(self._constellation_symbol,
                                 list(product(mapping_array, repeat=2))))

def ofdm_tx(x, nfft, nsc, cp_length):
    """ OFDM Transmit signal generation.
    Parameters
    ----------
    x : 1D ndarray of complex floats
        Input signal
    nfft : int
        fft size
    cp_length: int
        Length of CP
    Returns
    -------
    x: 1D array of complex floats
        OFDM modulated signal
    """
    nfft = float(nfft)
    nsc = float(nsc)
    cp_length = float(cp_length)
    ofdm_tx_signal = array([])

    for i in range(0, shape(x)[1]):
        symbols = x[:,i]
        ofdm_sym_freq = zeros(nfft, dtype=complex)
        ofdm_sym_freq[1:(nsc/2)+1] = symbols[nsc/2:]
        ofdm_sym_freq[-(nsc/2):] = symbols[0:nsc/2]
        ofdm_sym_time = ifft(ofdm_sym_freq)
        cp = ofdm_sym_time[-cp_length:]
        ofdm_tx_signal = concatenate((ofdm_tx_signal, cp, ofdm_sym_time))

    return ofdm_tx_signal

def ofdm_rx(y, nfft, nsc, cp_length):
    """ OFDM Receive Signal Processing.
    Parameters
    ----------
    y : 1D ndarray of complex floats
        Received complex symbols (shape: num_receive_antennas x 1)
    nfft :  int
        fft size
    nsc : 

    cp_length: int
        Length of CP
    Returns
    -------
    x_hat: 1D array of complex floats
        OFDM demodulated signal
    """

    num_ofdm_symbols = int(len(y)/(nfft + cp_length))
    x_hat = zeros([nsc, num_ofdm_symbols], dtype=complex)

    for i in range(0, num_ofdm_symbols):
        ofdm_symbol = y[i*nfft + (i+1)*cp_length:(i+1)*(nfft + cp_length)]
        symbols_freq = fft(ofdm_symbol)
        x_hat[:,i] = concatenate((symbols_freq[-nsc/2:], symbols_freq[1:(nsc/2)+1]))

    return x_hat

def mimo_ml(y, h, constellation):
    """ MIMO ML Detection.
    Parameters
    ----------
    y : 1D ndarray of complex floats
        Received complex symbols (shape: num_receive_antennas x 1)
    h : 2D ndarray of complex floats
        Channel Matrix (shape: num_receive_antennas x num_transmit_antennas)
    constellation : 1D ndarray of complex floats
        Constellation used to modulate the symbols
    Returns
    -------
    x_r: 2D array of complex floats
        estimated MIMI signal
    """
    m = len(constellation)
    x_ideal = array([tile(constellation, m), repeat(constellation, m)])
    y_vector = tile(y, m*m)
    min_idx = argmin(sum(abs(y_vector - dot(h, x_ideal)), axis=0))
    x_r = x_ideal[:, min_idx]

    return x_r
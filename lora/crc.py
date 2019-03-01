""" LPWAN Simulator: Cyclic redundancy check (CRC)
============================================
Utilities (:mod:`lora.crc`)
============================================
.. autosummary::
   :toctree: generated/ 
   set_div              -- Set divisor of the CRC  
   crc_remainder        -- Calculates the CRC remainder of a string of bits.
   crc_check            -- Calculates the CRC check of a string of bits.
   
"""

class crc:
    """ Cyclic redundancy check (CRC)
    Generates an CRC error detecting code based on an inputted message
    and divisor in the form of a polynomial representation.    
    |category /LoRa
    |keywords lora
    
    
    \param [IN] in_msg: The input message of which to generate the output code
    \param [IN] The divisor in polynomial form. For example, if the polynomial
            of x^3 + x + 1 is given, this should be represented as '1011' in
            the div argument.
    \param [IN] initial_filler: 
            default: '0'
    \param [OUT] data + crc    
        
    """
    def __init__(self, div, initial_filler='0'):
        self.div = div
        self.initial_filler = initial_filler
    
    """ Set divisor """
    def setDiv(self, div):
        self.div = div
        return(self)
    
    """ Set initial filter """
    def setInitial(self, initial_filler):
        self.initial_filler = initial_filler
        return(self)
        
    def crc_remainder(self, in_msg, initial_filler):
        """ Calculates the CRC remainder of a string of bits using a chosen polynomial.
        initial_filler should be '1' or '0.
        Parameters
        ----------
        in_msg : list
            string of bit
        initial_filler: list
            for generate initial padding
        Returns
        -------
        crc_msg: list
            crc message in list of bit
        """         
        msg=''.join(str(i) for i in in_msg)    # convert list [1,0,1,0] -> string '1010'
        len_input = len(msg)
        initial_padding = initial_filler * (len(self.div) - 1)
        msg_padded = list(msg + initial_padding)
        self.div = self.div.lstrip('0')
        while '1' in msg_padded[:len_input]:
            cur_shift = msg_padded.index('1')
            for i in range(len(self.div)):
                if self.div[i] == msg_padded[cur_shift + i]:
                    msg_padded[cur_shift + i] = '0'
                else:
                    msg_padded[cur_shift + i] = '1'
        crc= ''.join(msg_padded)[len_input:]
        crc_msg = list(msg + crc)
        return(crc_msg)
    
    def crc_check(self, in_msg, check_value):
        """ Calculates the CRC check of a string of bits using a chosen polynomial.
        initial_filler should be '1' or '0'.
        Parameters
        ----------
        in_msg : list
            string of bit
        check_value: list
            initial padding
        Returns
        -------
        crc_check: bool
            Result of crc check (True of False)
        """         
        len_input = len(in_msg)
        initial_padding = check_value
        msg_padded = list(in_msg + initial_padding)
        self.div = self.div.lstrip('0')
        while '1' in msg_padded[:len_input]:
            cur_shift = msg_padded.index('1')
            for i in range(len(self.div)):
                if self.div[i] == msg_padded[cur_shift + i]:
                    msg_padded[cur_shift + i] = '0'
                else:
                    msg_padded[cur_shift + i] = '1'
            if '1' not in ''.join(msg_padded)[len_input:]:
                return True
            else:
                return False
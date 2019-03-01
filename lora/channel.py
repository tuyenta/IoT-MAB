""" LPWAN Simulator: Simulate the propagation channel between the devices in the wireless network     
============================================
Utilities (:mod:`lora.channel`)
============================================
.. autosummary::
   :toctree: generated/   
   awgn                 -- Addditive White Gaussian Noise (AWGN) Channel.
   simpleRayleigh       -- Simple Rayleigh fading Channel.
   
"""

# Import Library
from numpy import abs, sqrt 
from numpy.random import randn, normal

def awgn(input_signal, snr_dB, rate=1.0):
    """
    Addditive White Gaussian Noise (AWGN) Channel.
    Parameters
    ----------
    input_signal : 1D ndarray of floats
        Input signal to the channel.
    snr_dB : float
        Output SNR required in dB.
    rate : float
        Rate of the a FEC code used if any, otherwise 1.
    Returns
    -------
    output_signal : 1D ndarray of floats
        Output signal from the channel with the specified SNR.
    """

    avg_energy = sum(abs(input_signal) * abs(input_signal))/len(input_signal)
    snr_linear = 10**(snr_dB/10.0)
    noise_variance = avg_energy/(2*rate*snr_linear)
    if isinstance(input_signal[0], complex):
        noise = (sqrt(noise_variance) * randn(len(input_signal))) + (sqrt(noise_variance) * randn(len(input_signal))*1j)
    else:
        noise = sqrt(2*noise_variance) * randn(len(input_signal))

    output_signal = input_signal + noise

    return output_signal

def simpleRayleigh(input_signal, snr_dB, rate=1.0):
    """
    Simple Rayleigh fading Channel.
    Parameters
    ----------
    input_signal : 1D ndarray of floats
        Input signal to the channel.
    snr_dB : float
        Output SNR required in dB.
    rate : float
        Rate of the a FEC code used if any, otherwise 1.
    Returns
    -------
    output_signal : 1D ndarray of floats
        Output signal from the channel with the specified SNR.
    """

    avg_energy = sum(abs(input_signal) * abs(input_signal))/len(input_signal)
    snr_linear = 10**(snr_dB/10.0)
    noise_variance = avg_energy/(2*rate*snr_linear)
    ch_coeff=sqrt(normal(0,1)**2+normal(0,1)**2)/sqrt(2)

    if isinstance(input_signal[0], complex):
        noise = (sqrt(noise_variance) * randn(len(input_signal))) + (sqrt(noise_variance) * randn(len(input_signal))*1j)
    else:
        noise = sqrt(2*noise_variance) * randn(len(input_signal))

    output_signal = input_signal * ch_coeff + noise

    return output_signal

#def doppler_jakes(max_doppler, filter_length):
#    """
#    
#    Parameters
#    ----------
#    input_signal : 1D ndarray of floats
#        Input signal to the channel.
#    snr_dB : float
#        Output SNR required in dB.
#    rate : float
#        Rate of the a FEC code used if any, otherwise 1.
#    Returns
#    -------
#    output_signal : 1D ndarray of floats
#        Output signal from the channel with the specified SNR.
#    """
#    fs = 32.0*max_doppler
#    ts = 1/fs
#    m = arange(0, filter_length/2)
#
#    # Generate the Jakes Doppler Spectrum impulse response h[m]
#    h_jakes_left = (gamma(3.0/4) *
#                    pow((max_doppler/(pi*abs((m-(filter_length/2))*ts))), 0.25) *
#                    jn(0.25, 2*pi*max_doppler*abs((m-(filter_length/2))*ts)))
#    h_jakes_center = array([(gamma(3.0/4)/gamma(5.0/4)) * pow(max_doppler, 0.5)])
#    h_jakes = concatenate((h_jakes_left[0:filter_length/2-1],
#                     h_jakes_center, h_jakes_left[::-1]))
#    h_jakes = h_jakes*hamming(filter_length)
#    h_jakes = h_jakes/(sum(h_jakes**2)**0.5)
#    
#    #-----------------------------------------------------------------------------
#    jakes_psd_right = (1/(pi*max_doppler*(1-(freqs/max_doppler)**2)**0.5))**0.5
#    zero_pad = zeros([(fft_size-filter_length)/2, ])
#    jakes_psd = concatenate((zero_pad, jakes_psd_right[::-1],jakes_psd_right, zero_pad))
#    print (size(jakes_psd))
#    jakes_impulse = real(fftshift(ifft(jakes_psd, fft_size)))
#    h_jakes = jakes_impulse[(fft_size-filter_length)/2 + 1 : (fft_size-filter_length)/2 + filter_length + 1]
#    h_jakes = h_jakes*hamming(filter_length)
#    h_jakes = h_jakes/(sum(h_jakes**2)**0.5)
#    #-----------------------------------------------------------------------------
#    return h_jakes    



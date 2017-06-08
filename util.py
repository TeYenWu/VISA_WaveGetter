import numpy as np


def smooth(x,window_len=11,window='hanning'):
    """smooth the data using a window with requested size.
        
        This method is based on the convolution of a scaled window with the signal.
        The signal is prepared by introducing reflected copies of the signal
        (with the window size) in both ends so that transient parts are minimized
        in the begining and end part of the output signal.
        
        input:
        x: the input signal
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
        flat window will produce a moving average smoothing.
        
        output:
        the smoothed signal
        
        example:
        
        t=linspace(-2,2,0.1)
        x=sin(t)+randn(len(t))*0.1
        y=smooth(x)
        
        see also:
        
        numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
        scipy.signal.lfilter
        
        TODO: the window parameter could be the window itself if an array instead of a string
        NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
        """
    
    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."
    
    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."
    
    
    if window_len<3:
        return x
    
    
    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"
    
    
    s=np.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=np.ones(window_len,'d')
    else:
        w=eval('np.'+window+'(window_len)')
    
    y=np.convolve(w/w.sum(),s,mode='valid')
    return y

def get_pin_voltage(s):
    values = []
    s.write([0x24])
    
    for row in range(80):
        result = s.read(size=2)
        values.append(int((result[0] & 0x00FF) | ((result[1] & 0x000F) << 8)))

    return values


def get_waves_data(s, pin_list):
    sample_data = {}
    
    for i in pin_list:
        s.write([0x11, 0x01, chr(i)])
        print('pos: %d' % i)
        result = s.read(size=2)
        for j in pin_list:
            if pin_list.index(i) >= pin_list.index(j):
                continue
            if len(pin_list) > 3 and (pin_list.index(i) + pin_list.index(j)) != (len(pin_list) - 1):
                continue
            #print(i)
            #print(j)
            print('pos: %d' % i)
            
            s.write([0x11, 0x02, chr(j)])
            result = s.read(size=2)
            for k in pin_list:
                s.write([0x11, 0x00, chr(k)])
                result = s.read(size=2)
                s.flushInput()
                s.flushOutput()
                wave = []
                s.write([0x25])
                
                for byte_n in xrange(2000):
                    point = s.read(size=2)
                    v = from_bytes(point)
                    Vvalue = float((v-2048)*0.00244140625)
                    wave.append(Vvalue)
                
                wave[0] = wave[1]
                wave[-2] = wave[-1]
                wave_data = {
                    'rate' : 80000,
                    'volt' : 1,
                    'wave' : wave
                }
                sample_data['pos' + str(pin_list.index(i) + 1) + '_neg' + str(pin_list.index(j) + 1) + '_test' + str(pin_list.index(k) + 1)] = wave_data
    
    return sample_data

def from_bytes (data, big_endian = False):
    data = bytearray(data)
    if big_endian:
        data = reversed(data)
    num = 0
    for offset, byte in enumerate(data):
        num += byte << (offset * 8)
    return num


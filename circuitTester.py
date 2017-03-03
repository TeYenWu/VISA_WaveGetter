import json
import argparse
from scipy import signal
import numpy as np
import matplotlib.pyplot as plt

from math import log

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


class circuit_tester():
    def __init__(self, Hz=50, MaxV=1, sample_rate=80000, innerR=50, sampleUnit=1):
        self.Hz = Hz
        self.MaxV = MaxV
        self.halfV = float(MaxV) / 2
        self.rate = sample_rate
        self.innerR = innerR
        self.sampleUnit = sampleUnit



    def two_pin_discriminator(self, wave):
        element = 'unknown'
        value = None

        pos_samples = filter(lambda x: x > 0, wave)
        neg_samples = map(abs, filter(lambda x: x < 0, wave))

        pos_samples = sorted(pos_samples)[1:]
        neg_samples = sorted(neg_samples)[1:]

        pos_range = (max(pos_samples) - min(pos_samples)) / max(pos_samples)
        neg_range = (max(neg_samples) - min(neg_samples)) / max(neg_samples)
        print('pos range percentage: %f' % pos_range)
        print('neg range percentage: %f' % neg_range)

        if pos_range > 0.2 or neg_range > 0.2:
            #TODO: determine capacitor and inductor
            start = None
            count = 0
            for i in range(len(wave)): # mistake if capacitor not fully charged 
                #print(wave[i] * self.sampleUnit)
                if abs((wave[i] * self.sampleUnit) + self.halfV) <= 0.05:
                    #print('find start')
                    start = i
                    count = 0
                    continue
                if start == None: 
                    continue

                count += 1
                if count > 100:
                    break

            period_sample = self.rate / self.Hz
            period_sample = 1500 #don't know exact Hz and sample rate
            
            if start == None:
                # error if start not found
                return element, value

            end = start + period_sample / 2 - 10 
            half_wave = wave[start:end]

            out_of_bound = 0
            for i in range(len(half_wave)):
                lower = half_wave[0] + (half_wave[-1] - half_wave[0]) * i / len(half_wave)
                upper = half_wave[-1] + 0.01 #to tolerence noise
                s = half_wave[i]

                if s < lower or s > upper:
                    out_of_bound += 1

            if out_of_bound / len(half_wave) < 0.01:
                element = 'capacitor'
                value = self.caculate_C(half_wave)

        else:
            mean_pos = sum(pos_samples) / len(pos_samples)
            mean_neg = sum(neg_samples) / len(neg_samples)

            print('mean difference: %f' % abs(mean_pos - mean_neg))

            if abs(mean_pos - mean_neg) / max(mean_pos, mean_neg) > 0.3: # ?
                element = 'diode'
            else:
                element = 'resistance'
                value = self.caculate_R(wave)

        return element, value

    def caculate_C(self, wave, windowSize=3):
        sampleTime = 1.0 / self.rate
        #caculate t
        end = None
        for i in range(len(wave)):
            if sum(wave[i-windowSize:i+windowSize+1]) / (2 * windowSize + 1) > 0:
                end = i
                break

        print('sample Time: %f' % sampleTime)
        t = end * sampleTime
        print('t: %f' % t)

        return -t / (log(1.0 / 2) * self.innerR)

    def caculate_L(self, t):
        return -(log(1.0 / 2) * self.innerR) / t


    def caculate_R(self, wave):
        sampleTime = 1 / self.rate
        halfV = float(self.MaxV) / 2
        
        samples = []
        start = False
        for sample in wave: # no need
            if not start and sample > 0:
                samples.append(sample)
                start = True

            if start:
                if sample > 0:
                    print(sample * self.sampleUnit)
                    samples.append(sample)
                else:
                    break

        testV = sum(samples) / len(samples) * self.sampleUnit

        return self.innerR * testV / (self.MaxV - testV)



windowSize = 3

def two_pin_discriminator(data):
    wave = data['wave']
    #plt.plot(wave)
    #plt.show()
    
    element = 'unknown'

    pos_samples = []
    neg_samples = []
    start = False
    now = abs(wave[0]) / wave[0]
    change_num = 0
    for sample in wave:
        if now * sample < 0:
            start = True
            now = now * -1
            change_num += 1
            if change_num > 2:
                break
        
        if start: 
            if now > 0:
                pos_samples.append(sample)
            else:
                neg_samples.append(abs(sample))

        
    pos_samples = sorted(pos_samples)[1:]
    neg_samples = sorted(neg_samples)[1:]

    pos_range = (max(pos_samples) - min(pos_samples)) / max(pos_samples)
    neg_range = (max(neg_samples) - min(neg_samples)) / max(neg_samples)
    print('pos range percentage: %f' % pos_range)
    print('neg range percentage: %f' % neg_range)

    if pos_range > 0.2 or neg_range > 0.2:
        
        
        

        element = 'capacitor'
    else:
        mean_pos = sum(pos_samples) / len(pos_samples)
        mean_neg = sum(neg_samples) / len(neg_samples)

        print('mean difference: %f' % abs(mean_pos - mean_neg))
        if abs(mean_pos - mean_neg) / max(mean_pos, mean_neg) > 0.3:
            element = 'diode'
        else:
            element = 'resistance'

    
    '''old_sample = wave[0]
    for sample in wave:
        if sample - old_sample > 3 or sample - old_sample < -3:
            element = 'inductor'
            print(sample - old_sample)
        old_sample = sample
    
    element = 'capacitor'
    '''
    return element

def caculate_C(R, data, MaxV):
    wave = data['wave']
    sampleTime = 1.0 / data['rate']
    sampleUnit = data['volt']
    halfV = float(MaxV) / 2
    print(halfV)
    #caculate t
    start = None
    end = None
    
    #print('peak: ')
    #print(signal.find_peaks_cwt(data, np.arange(1, 10)))

    for i in range(len(wave)):
        print(wave[i] * sampleUnit)
        #print(abs((wave[i] * sampleUnit) + halfV))
        if abs((wave[i] * sampleUnit) + halfV) <= 0.05:
            print('find start')
            start = i
            continue
        if start == None: 
            continue

        if sum(wave[i-windowSize:i+windowSize+1]) / (2 * windowSize + 1) > 0:
            print('find end')
            end = i
            break
    plt.plot(wave[start-10:end+10])
    print('start: %d, end: %d' % (start, end))
    print('start value: %f, end value: %f' % (wave[start], wave[end]))
    print('sample Time: %f' % sampleTime)
    t = (end - start) * sampleTime
    print('t: %f' % t)
    return -t / (log(1.0 / 2) * R)

def caculate_L(R, t):
    return -(log(1 / 2) * R) / t


def caculate_R(innerR, data, MaxV):
    wave = data['wave']
    sampleTime = 1 / data['rate']
    sampleUnit = data['volt']
    halfV = MaxV / 2
    
    samples = []
    start = False
    for sample in wave:
        if not start and sample > 0:
            samples.append(sample)
            start = True

        if start:
            if sample > 0:
                print(sample * sampleUnit)
                samples.append(sample)
            else:
                break

    testV = sum(samples) / len(samples) * sampleUnit

    return innerR * testV / (MaxV - testV)





if __name__ == "__main__":
    #parser = argparse.ArgumentParser(description="Argument parser")
    #parser.add_argument("--data_file", type=str, help="input file name")

    #args = parser.parse_args()
    
    #with open(args.data_file, "r") as f:
        #data = json.load(f)

    data = json.load(open('result.json', 'r'))
    ct = circuit_tester()    
    element, value = ct.two_pin_discriminator(data[0][1:])
    print(element)
    print(value)

    #print(caculate_C(R, data[0]['pos'], MaxV))
    #print(caculate_R(R, data[0]['pos'], MaxV))


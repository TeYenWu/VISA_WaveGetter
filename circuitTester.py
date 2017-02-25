import json
import argparse
from scipy import signal
import numpy as np
import matplotlib.pyplot as plt

from math import log

Hz = 5
V = 1

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
        #old_sample = wave[0]
        #total_range = 
        #for sample in wave:
            

        element = 'capacitor'
    else:
        mean_pos = sum(pos_samples) / len(pos_samples)
        mean_neg = sum(neg_samples) / len(neg_samples)

        print('mean difference: %f' % abs(mean_pos - mean_neg))
        if abs(mean_pos - mean_neg) > 1:
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
    parser = argparse.ArgumentParser(description="Argument parser")
    parser.add_argument("--data_file", type=str, help="input file name")

    args = parser.parse_args()
    
    with open(args.data_file, "r") as f:
        data = json.load(f)

    two_pin_discriminator(data[0]['pos'])
    R = 50
    MaxV = 0.5
    #print(caculate_C(R, data[0]['pos'], MaxV))
    #print(caculate_R(R, data[0]['pos'], MaxV))


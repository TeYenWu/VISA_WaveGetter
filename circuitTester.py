from scipy import signal
from math import log
import numpy as np
import matplotlib.pyplot as plt
import json
import argparse
import visa
import serial
import serial.tools.list_ports
import time
import os
import math
import sys

from util import get_pin_voltage, get_waves_data, smooth
import model

STDIN = 0
STDOUT = 1
STDERR = 2

def get_command():
    get = os.read(STDIN, 100)
    get = str(get).split('\n')[0]
    return get.split(':')

class circuit_tester():
    def __init__(self, Hz=50, MaxV=1, sample_rate=80000, innerR=160, sampleUnit=1, direct=False, dynamic_volt=False):
        self.Hz = Hz
        self.MaxV = MaxV
        self.halfV = float(MaxV) / 2
        self.rate = sample_rate
        self.innerR = innerR
        self.sampleUnit = sampleUnit
        
        #plt initialize
        plt.ion()
        plt.show()
        plt.axis([0, 2000, -0.5, 0.5])
        plt.plot([])

        
        #serial initialization for wave data from breadboard
        if direct:
            print('serial initializing...')
            while True:
                command = get_command()
                if command[0] = "start":
                    break
            port_name = command[1]
            self.s = serial.Serial(port_name, 500000)
            self.s.flushInput()
            self.s.flushOutput()

        #visa initialization for controlling function generator
        
        if dynamic_volt:
            print('visa initializing...')
        
            rm = visa.ResourceManager()
            self.func_gen = rm.open_resource('TCPIP::10.0.1.42::INSTR')
            self.func_gen.write('SOURce1:VOLTage:HIGH 0.25V')
            self.func_gen.write('SOURce1:VOLTage:LOW -0.25V')
        
        #loading classification model
        self.models = {}
        with open ('models.list', 'r') as f:
            for line in f:
                model_name = line.strip()
                print('loading model: %s' % model_name)
                self.models[model_name] =model.RF(model_dir=model_name, preTrained=True) 
    
        

    def start_tester(self):
        #pin_lists = [[0, 8], [0, 8], [0, 8], [0, 8], [0, 8], [0, 1, 2], [0, 1, 2], [0, 1, 2], [0, 1, 2], [0, 1, 2], [0, 1, 2], [0, 1, 2, 3, 11, 10, 9, 8], [0, 1, 2, 3, 11, 10, 9, 8], [0, 1, 2, 3, 11, 10, 9, 8], [0, 1, 2, 3, 11, 10, 9, 8], [0, 1, 2, 3, 11, 10, 9, 8], [0, 1, 2, 3, 11, 10, 9, 8], [0, 1, 2, 3, 11, 10, 9, 8], [0, 1, 2, 3, 11, 10, 9, 8]]
        
        # pin_lists = [[4,7], [4,11], [7,15], [15,13], [13,12],[12,11],[12,11]] hao
        # pin_lists = [[1,2,3,4,9,10,11,12], [12,15],[15,14], [13,10],[14,11], [15, 13], [13, 10], [9,4], [2,11], [3,0],[0,2],[3,7],[7,4]]
        #pin_lists = [[4, 5, 6, 7, 15, 14, 13, 12], [0, 2], [2, 10], [8, 10], [10, 13], [8, 15], [7, 12], [12, 14]]
        #pin_lists = [[0, 1, 2, 3, 11, 10, 9, 8]]
        '''
        pin_lists = [[0, 8]]
        raw_input('Tester start...')
        for pin_list in pin_lists:
            #pin_list = json.loads(raw_input('pin_list: '))
            
            element, value = self.test(pin_list)
            title = element
            if value != None:
                title += (' %s' % value)

            raw_input('Detected: ' + title)
        '''
        os.write(1, "ready")
        
        while True:
            command = get_command()

            if command[0] == "scan":
                pin_matrix = self.PLS_scan()
                os.write(STDOUT, json.dumps(pin_matrix))
            elif command[0] == "pin_list":
                pin_list = map(int, command[1].split(','))
                element, value = self.test(pin_list)
                os.write(STDERR, "CT: %s %s" % (element, value)) if value != None else os.write(2, "CT: %s" % element)
                os.write(STDOUT, "%s,%s" % (element, value))
            elif command[0] == "end":
                os.write(STDOUT, "CircuitTester closed")
                break
            else:
                os.write(STDOUT, "illegal command")

    def PLS_scan(self):
        voltages = get_pin_voltage(self.s)
        return ','.join(voltages)
        

    def set_voltage(self, V):
        self.func_gen.write('SOURce1:VOLTage:HIGH %.2fV' % (float(V) / 2))
        self.func_gen.write('SOURce1:VOLTage:LOW -%.2fV' % (float(V) / 2))
        time.sleep(0.1)

    def test(self, pin_list=[0, 8]):
        print("data collecting ...")
        waves = get_waves_data(self.s, pin_list)

        #plt.clf()
        #plt.ylim([-0.5,0.5])
        #for key in waves.keys():
        #    plt.plot(waves[key]['wave'])
        
        element, value = self.discriminate(waves, len(pin_list))
    
        #if breakage, raise voltage to test whether it reach the working voltage
        if len(pin_list) == 2 and element == 'breakage':
             self.set_voltage(2)
            
             waves = get_waves_data(self.s, pin_list)
             element, value = self.discriminate(waves, len(pin_list), test_V='2V')
            
             self.set_voltage(0.5)

        plt.clf()
        for key in waves.keys():
            plt.plot((np.array(waves[key]['wave'])))
            
        title = element
        if value != None:
            title += (' %s' % value)
        plt.title(title, fontsize=60)

        
        return element, value

    def discriminate(self, waves, pin_num, test_V='0.5V'):
        element = 'unknown'
        
        model_name = '%dpin_Model' % pin_num
        if pin_num == 2:
            model_name += ('_' + test_V)

        
        if model_name not in self.models.keys():
            print('No suitable model for %s.' % model_name)
        element = self.models[model_name].test(waves)
        
        #caculate two pin value
        
        value = None
        if element == 'capacitor':
            value = self.calculate_C(waves['pos1_neg2_test2'])
            value = str(int(value)) + '$\mu$F'

        elif element == 'inductor':
            value = self.calculate_L(waves['pos1_neg2_test1'])
            value = str(int(value)) + 'mH'
        
        elif element == 'resistence':
            value = self.calculate_R(waves['pos1_neg2_test1'])
            value = str(int(value)) + '$\Omega$'
        
        return element, value

    def calculate_C(self, data, windowSize=3):
        wave = data['wave']
        sampleTime = 1.0 / self.rate
  
        minV, maxV = 0., 0.
        for i in range(len(wave)):
            if i < 2:
                continue
            value = (sum(wave[i-windowSize:i+windowSize+1]) / (2 * windowSize + 1))
            if (value < minV):
                minV = value
            if (value > maxV):
                maxV = value

        zeroV = maxV + minV
        
        findStart, findMax = 0, 0
        start, end, maxIdx, endmaxIdx = None, None, None, len(wave) - 1
        for i in range(len(wave)):
            if i < 2:
                continue

            value = wave[i] * self.sampleUnit
            if abs(value - maxV) <= 0.02 and findMax == 0:
                maxIdx = i 
                findMax = 1

            if value < 0 and findMax == 1:
                endmaxIdx = i - 1
                findMax = 2

            if abs(value - maxV / 2) <= 0.02 and findStart == 0:
                # print('find start')
                start = i
                findStart = 1
            
            if abs(value) <= 0.02 and findStart == 1:
                # print('find end')
                end = i 
                findStart = 2

            if findMax == 2 and findStart == 2:
                break

        if start == None or end == None:
            start = maxIdx
            end = endmaxIdx
        
        logWave, xAxis = [], [] 
        #linear programming
        if start != None and end != None:
            for i in range(end-start):
                logWave.append(np.log((wave[i + start] * self.sampleUnit)-zeroV))
                xAxis.append(i)

            if len(xAxis) == 0:
                print('here')
                return None
            m,b = np.polyfit(xAxis,logWave,1)

            return -sampleTime / (140 * m) * 1000000
        return None

    def calculate_L(self, data, windowSize=3):
        wave = data['wave']
        sampleTime = 1.0 / self.rate

        start = None
        end = None
        minV = 0.
        maxV = 0.
        for i in range(len(wave)):
            value = (sum(wave[i-windowSize:i+windowSize+1]) / (2 * windowSize + 1))
            if (value < minV):
                minV = value
            if (value > maxV):
                maxV = value
        #print('minV: %f, maxV: %f' % (minV,maxV))
        #zeroV = maxV + minV
        logWave = []
        xAxis = []
        for i in range(len(wave)):
            value = wave[i] * self.sampleUnit
            if abs(value - maxV) <= 0.05 :
                # print('find start')
                start = i
                continue
            
            if abs(value - minV) <= 0.05 and start != None:
                # print('find end')
                end = i
                break
        for i in range(end-start):
            logWave.append(np.log((wave[i + start] * self.sampleUnit)-minV))
            xAxis.append(i)
        fit = np.polyfit(xAxis,logWave,1)
        m,b = np.polyfit(xAxis,logWave,1)
        print('m: %f b: %f' %(m, b))
        fit_fn = np.poly1d(fit)
        plt.plot(xAxis, fit_fn(xAxis))
        plt.plot(logWave)

        return -sampleTime * self.innerR / m

    def calculate_R(self, data, windowSize=10):
        wave = (np.array(data['wave']))
        sampleTime = 1 / self.rate
        minV = 0.
        maxV = 0.
        min_samples = []
        max_samples = []
        for sample in wave:
            if sample < 0 and abs(sample) > 0.1:
                min_samples.append(float(sample))
            elif sample > 0 and abs(sample) > 0.1:
                max_samples.append(float(sample))
        
        numSample = int(len(max_samples) * 0.01)
        max_samples.sort()
        min_samples.sort()
        std = np.std(max_samples)
        mean = np.mean(max_samples)
#        print('before: %d' % len(max_samples))
        outlier_num = 20
        #max_samples = [s for s in max_samples if s < mean + std and s > mean - std]
        #maxV = sum(max_samples[len(max_samples) - numSample -outlier_num:len(max_samples)-outlier_num]) / numSample
        maxV = (sum(max_samples[outlier_num:numSample+outlier_num]) + sum(max_samples[len(max_samples) - numSample -outlier_num:len(max_samples)-outlier_num])) / (numSample * 2)
        minV = (sum(min_samples[outlier_num:numSample+outlier_num]) + sum(min_samples[len(min_samples) - numSample -outlier_num:len(min_samples)-outlier_num])) / (numSample * 2)
#        print('std: %f' % std)
#        print('after: %d' % len(max_samples))
#        maxV = (max(max_samples) + min(max_samples)) / 2
        #maxV = np.median(max_samples)
#        minV = (max(min_samples) + min(min_samples)) / 2

#        for i in range(len(wave)):
#            value = (sum(wave[i-windowSize:i+windowSize+1]) / (2 * windowSize + 1))
#            if (value < minV):
#                minV = value
#            if (value > maxV):
#                maxV = value
        testV = (maxV - minV)/2.
#       
#        maxV = maxV + 0.005
#        minV = minV + 0.005
#
#        halfV=0.49
#        samples = []
#        start = False
#        for sample in wave: # no need
#            if not start and abs(sample - minV) < 0.02:
#                samples.append(float(sample))
#                start = True
#            
#            if start:
#                if abs(sample - minV) < 0.01:
#                    #print(sample * self.sampleUnit)
#                    samples.append(sample)
#                else:
#                    break

#        testV = -(sum(samples) / float(len(samples))  - middleV)
#        testV = maxV
#        print(testV)
#        print('maxV: %f' % maxV)
#        print('min: %f' % minV)
#        print('middle: %f' % middleV)
        #print(self.MaxV)
        
        v1 = (self.innerR * (0.5 + minV)- 52)/ -(0.5 + minV)
        v2 = (self.innerR * maxV- 27)/ (0.5 - maxV)
        v3 = (self.innerR * testV - 27) / (0.5 - testV)
        return (v3)

def test_error_rate(ct, testType='resistence', upper=0.05):    
    data_dir = '2-pin'
    sub_dirs = [o for o in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir,o))]
    nan, over, total, none, numUpper = 0, 0, 0, 0, 0
    error_rates = []

    for sub_dir in sub_dirs:
        label = sub_dir.split('_')[0]
        if label != testType:
            continue
        value = sub_dir.split('_')[1]
        value = float(value) if testType == 'resistence' else float(value[:-1])

        data = json.load(open(os.path.join(data_dir, sub_dir, 'data.json'), 'r'))
        for d in data:
            total += 1
            if testType == 'resistence':
                test = ct.calculate_R(d['pos1_neg2_test1'])
            elif testType == 'capacitor':
                test = ct.calculate_C(d['pos1_neg2_test2'])
            if test == None:
                none += 1
                print('value: %f, None' % (value))
                continue

            if math.isnan(test):
                nan += 1
                continue

            error = abs(value - test) / value
            print('value: %f, test: %f, error rate: %f' % (value, test, error))
            #if error > 0.3:
            #    plt.plot(d['pos1_neg2_test1']['wave'])
            #    plt.show()
            if value == 220 or value == 120:
                continue
            if error > upper:
                numUpper += 1
            error_rates.append(error)

    print('average error rate: %f, max: %f, std: %f' % (np.mean(error_rates), max(error_rates), np.std(error_rates)))
    print('none: %f, nan: %f, over: %f, total: %f, upper_exceed: %f' % (none, nan, over, total, numUpper))

if __name__ == '__main__':
    ct = circuit_tester(direct=True)
    #test_error_rate(ct)
    ct.start_tester()

    

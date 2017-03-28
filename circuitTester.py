from scipy import signal
from math import log
import numpy as np
import matplotlib.pyplot as plt
import json
import argparse
import visa
import serial
import serial.tools.list_ports

from util import get_waves_data
import model

class circuit_tester():
    def __init__(self, Hz=50, MaxV=1, sample_rate=80000, innerR=50, sampleUnit=1):
        self.Hz = Hz
        self.MaxV = MaxV
        self.halfV = float(MaxV) / 2
        self.rate = sample_rate
        self.innerR = innerR
        self.sampleUnit = sampleUnit
        
        #serial initialization for wave data from breadboard
        print('serial initializing...')
        ports = list(serial.tools.list_ports.comports())
        self.s = serial.Serial("/dev/cu.SLAB_USBtoUART", 500000, parity=serial.PARITY_EVEN)
        self.s.flushInput()
        self.s.flushOutput()

        #visa initialization for controlling function generator
        print('visa initializing...')
        rm = visa.ResourceManager()
        self.func_gen = rm.open_resource('TCPIP::10.0.1.57::INSTR')
        self.func_gen.write('SOURce1:VOLTage:HIGH 0.25V')
        self.func_gen.write('SOURce1:VOLTage:LOW -0.25V')
        
        #loading classification model
        self.models = {}
        with open ('models.list', 'r') as f:
            for line in f:
                model_name = line.strip()
                print('loading model: %s' % model_name)
                self.models[model_name] =model.RF(model_dir=model_name, preTrained=True) 
        #self.models['2pin'] = model.RF(model_dir='2pin_Model_combine', data_dir='2-pin-combine', preTrained=True)
        #self.models['2pin_0.5V'] = model.RF(model_dir='2pin_Model', data_dir='2-pin', preTrained=True)
        #self.models['2pin_2V'] = model.RF(model_dir='2pin_Model_2V', data_dir='2-pin-2V', preTrained=True)
    
    def start_tester(self):
        pass    
    
    def test(self, pin_list=[0, 8]):
        waves = get_waves_data(self.s, pin_list)
        element = self.discriminate(waves, len(pin_list))
    
        #if breakage, raise voltage to test whether it reach the working voltage
        if len(pin_list) == 2 and element == 'breakage':
            self.func_gen.write('SOURce1:VOLTage:HIGH 1V')
            self.func_gen.write('SOURce1:VOLTage:LOW -1V')

            waves = get_waves_data(self.s, pin_list)
            element = self.discriminate(waves, len(pin_list), test_V='2V')
            
            self.func_gen.write('SOURce1:VOLTage:HIGH 0.25V')
            self.func_gen.write('SOURce1:VOLTage:LOW -0.25V')

        #caculate two pin value
        value = None
        if element == 'capacitor':
            pass

        if element == 'inductor':
            pass

        if element == 'resistence':
            pass

        return element, value

    def discriminate(self, waves, pin_num, test_V='0.5V'):
        element = 'unknown'
        value = None
    
        model_name = '%dpin_Model' % pin_num
        if pin_num == 2:
            model_name += ('_' + test_V)

        
        if model_name not in self.models.keys():
            print('No suitable model for %s.' % model_name)
        print(model_name)
        element = self.models[model_name].test(waves)
            
        return element




if __name__ == "__main__":
    #parser = argparse.ArgumentParser(description="Argument parser")
    #parser.add_argument("--data_file", type=str, help="input file name")

    #args = parser.parse_args()
    
    ct = circuit_tester()
    #element, value = ct.test()
    #print(element)
    

import visa
import numpy as np
from scipy import spatial
import time
import sys
import json
import os
import matplotlib.pyplot as plt
import argparse
import serial
import serial.tools.list_ports
from serialPortTest import from_bytes
from util import get_waves_data

parser = argparse.ArgumentParser(description="Argument parser")
parser.add_argument('--element', type=str, help='element name')
parser.add_argument('--spec', type=str, help='specification name')
parser.add_argument('--sample_num', type=int, help='sample number')
parser.add_argument('--append', action='store_true', help='wether to append on origin data')
parser.set_defaults(append=False)

args = parser.parse_args()


ports = list(serial.tools.list_ports.comports())
s = serial.Serial("/dev/cu.SLAB_USBtoUART", 500000, parity=serial.PARITY_EVEN)
s.flushInput()
s.flushOutput()
print('ready')

filepath = os.path.join(os.getcwd(), args.element)
if not os.path.exists(filepath):
    os.mkdir(filepath)

filepath = os.path.join(filepath, args.spec)
if not os.path.exists(filepath):
    os.mkdir(filepath)


os.chdir(filepath)


try:
    #data structure: [{'pos': {'wave': [wave data ...], 'rate': sample rate}, 'neg': {'wave': [wave data ...], 'rate': sample rate}}]
    data = []
    if args.append:
        if os.path.exists(os.path.join(filepath, 'data.json')):
            with open('data.json', 'r') as f:
                data = json.load(f)
        else:
            print('WARNING: data.json not exist')

    
    started = False
    #probe_list = [(0, 8), (1, 9), (2, 10), (3, 11)]
    pin_list = [9, 12]
    for sample_id in range(args.sample_num):
        #while raw_input('press enter to get element data...'):
        
        print('start %d' % sample_id)
        '''
        sample_data = {}
        
        for i, j in probe_list:
            s.write([0x11, 0x01, chr(i)])
            result = s.read(size=2)
            #print(i) 
            s.write([0x11, 0x02, chr(j)])
            result = s.read(size=2)
            #print(j)
            for k in pin_list:
            
                s.write([0x11, 0x00, chr(k)])
                result = s.read(size=2)
                s.flushInput()
                s.flushOutput()
                wave = []
                s.write([0x23])
                
                #print("pos_pin: %d, neg_pin: %d, test_pin: %d" % (i, j, k))
                    
                for byte_n in xrange(2000):
                    point = s.read(size=2)
                    v = from_bytes(point)
                    Vvalue = float((v-2048)*0.00244140625)
                    wave.append(Vvalue)
                    
                wave_data = {
                    'rate' : 80000,
                    'volt' : 1,
                    'wave' : wave
                }
                #print('pos' + str(pin_list.index(i) + 1) + '_neg' + str(pin_list.index(j) + 1) + '_test' + str(pin_list.index(k) + 1))
                sample_data['pos' + str(pin_list.index(i) + 1) + '_neg' + str(pin_list.index(j) + 1) + '_test' + str(pin_list.index(k) + 1)] = wave_data
    #plt.plot(wave_data['wave'])
    #plt.show()
        '''

        data.append(get_waves_data(s, pin_list))

    with open('data.json', 'w') as f:
        json.dump(data, f)

except KeyboardInterrupt:
    with open('data.json', 'w') as f:
        json.dump(data, f)
        print("data have been saved")


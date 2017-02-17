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

parser = argparse.ArgumentParser(description="Argument parser")
parser.add_argument('--element', type=str, help='element name')
parser.add_argument('--spec', type=str, help='specification name')
parser.add_argument('--pin_num', type=int, help='pin number')
parser.add_argument('--sample_num', type=int, help='sample number')
parser.add_argument('--start_pos_pin',type=int, default=1, help='postive pin to start with')
parser.add_argument('--start_neg_pin', type=int, default=1, help='negative pin to start with')
parser.add_argument('--start_test_pin', type=int, default=1, help='test pin to start with')

args = parser.parse_args()

'''
rm = visa.ResourceManager()
rm.list_resources()
inst = rm.open_resource('TCPIP::10.0.1.47::INSTR')
inst.write('DATA:SOURCE CH1')
print(inst.query("*IDN?"))

inst.write('HORizontal:RECOrdlength 20000');
inst.write('DATa:STARt 1');
inst.write('DATa:STOP 20000');
'''

ports = list(serial.tools.list_ports.comports())
s = serial.Serial("/dev/cu.SLAB_USBtoUART", 115200, parity=serial.PARITY_EVEN)
s.flushInput()
s.flushOutput()


filepath = os.path.join(os.getcwd(), args.element)
if not os.path.exists(filepath):
    os.mkdir(filepath)

filepath = os.path.join(filepath, args.spec)
if not os.path.exists(filepath):
    os.mkdir(filepath)


os.chdir(filepath)


try:
    #data structure: [{'pos': {'wave': [wave data ...], 'rate': sample rate}, 'neg': {'wave': [wave data ...], 'rate': sample rate}}]
    '''
    if os.path.exists(os.path.join(filepath, 'data.json')):
        with open('data.json', 'r') as f:
            data = json.load(f)
    else:
        data = []
    '''
    data = []

    started = False
    pin_list = [0, 1, 2, 3, 11, 10, 9, 8]
    for sample_id in pin_list:
        while raw_input('press enter to get element data...'):
            pass

        '''
        if not started and len(data) > 0:
            sample_data = data[-1]
        else:
            sample_data = {}
        '''
        sample_data = {}

        for i in pin_list:
            s.write([0x11, 0x01, chr(i), 0x00])
            result = s.read(size=1)
            if from_bytes(result) != 1:
                break

            for j in pin_list:
                if i >= j:
                    continue
                s.write([0x11, 0x02, chr(j), 0x00])
                result = s.read(size=1)
                if from_bytes(result) != 1:
                    break
                for k in pin_list:
                    #test_pin = k + 1
                    #pos_pin = i + 1
                    #neg_pin = i + j + 2
                    if k == j:
                        continue

                    s.write([0x11, 0x00, chr(k), 0x00])
                    result = s.read(size=1)
                    if from_bytes(result) != 1:
                        break
                    s.flushInput()
                    s.flushOutput()
                    wave = []
                    s.write([0x23])
                    
                    '''
                    if not started:
                        if pos_pin < args.start_pos_pin or neg_pin < args.start_neg_pin or test_pin < args.start_test_pin:
                            continue
                        started = True
                    '''

                    print("pos_pin: %d, neg_pin: %d, test_pin: %d" % (i, j, k))
                    
                    for byte_n in xrange(2000):
                        #print('in_waiting:' + str(s.in_waiting)) 
                        data = s.read(size=2)
                        v = from_bytes(data)
                        Vvalue = float((v-2048)*0.00244140625)
                        wave.append(Vvalue)
                        #print(byte_n) 
                    
                    wave_data = {
                        'rate' : 100000,
                        'volt' : 40,
                        #'pos' : inst.query("CH1:POSition?"),
                        #'offset' : inst.query("CH1:OFFSet?"),
                        #'deskew' : inst.query("CH1:DESKew?"),
                        #'bandwidth' : inst.query("CH1:BANDWIDTH?"),
                        #'probe' : inst.query("CH1:PRObe?"),
                        'wave' : wave 
                    }
                    #print(wave_data)
                    #print('%d, %d, %d' % )
                    sample_data['pos' + str(pin_list.index(i) + 1) + '_neg' + str(pin_list.index(j) + 1) + '_test' + str(pin_list.index(k) + 1)] = wave_data
                    plt.plot(wave_data['wave'])
                    plt.show()

        data.append(sample_data)

    with open('data.json', 'w') as f:
        json.dump(data, f)
                
except KeyboardInterrupt:
    with open('data.json', 'w') as f:
        json.dump(data, f)
        print("data have been saved")



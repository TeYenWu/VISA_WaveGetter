import visa
import numpy as np
from scipy import spatial
import time
import sys
import json
import os
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser(description="Argument parser")
parser.add_argument('--element', type=str, help='element name')
parser.add_argument('--spec', type=str, help='specification name')
parser.add_argument('--pin_num', type=int, help='pin number')
parser.add_argument('--sample_num', type=int, help='sample number')
parser.add_argument('--start_pos_pin',type=int, default=1, help='postive pin to start with')
parser.add_argument('--start_neg_pin', type=int, default=1, help='negative pin to start with')
parser.add_argument('--start_test_pin', type=int, default=1, help='test pin to start with')

args = parser.parse_args()


rm = visa.ResourceManager()
rm.list_resources()
inst = rm.open_resource('TCPIP::10.0.1.47::INSTR')
inst.write('DATA:SOURCE CH1')
print(inst.query("*IDN?"))

inst.write('HORizontal:RECOrdlength 20000');
inst.write('DATa:STARt 1');
inst.write('DATa:STOP 20000');

filepath = os.path.join(os.getcwd(), args.element)
if not os.path.exists(filepath):
    os.mkdir(filepath)

filepath = os.path.join(filepath, args.spec)
if not os.path.exists(filepath):
    os.mkdir(filepath)


os.chdir(filepath)


try:
    #data structure: [{'pos': {'wave': [wave data ...], 'rate': sample rate}, 'neg': {'wave': [wave data ...], 'rate': sample rate}}]
    if os.path.exists(os.path.join(filepath, 'data.json')):
        with open('data.json', 'r') as f:
            data = json.load(f)
    else:
        data = []

    started = False
    for sample_id in range(args.sample_num):
        if not started and len(data) > 0:
            sample_data = data[-1]
        else:
            sample_data = {}
        
        for i in range(args.pin_num):
            for j in range(args.pin_num - i - 1):
                for k in range(args.pin_num):
                    test_pin = k + 1
                    pos_pin = i + 1
                    neg_pin = i + j + 2
                    if test_pin == neg_pin:
                        continue
                    if not started:
                        if pos_pin < args.start_pos_pin or neg_pin < args.start_neg_pin or test_pin < args.start_test_pin:
                            continue
                        started = True
    
                    print("pos_pin: %d, neg_pin: %d, test_pin: %d" % (pos_pin, neg_pin, test_pin))
                    while input('Enter Y to gather wave data...') == 'Y':
                        pass
                
                    wave_data = {
                        'rate' : float(inst.query('HORizontal:SAMPLERate?')),
                        'volt' : float(inst.query('CH1:VOLts?')),
                        'pos' : inst.query("CH1:POSition?"),
                        'offset' : inst.query("CH1:OFFSet?"),
                        'deskew' : inst.query("CH1:DESKew?"),
                        'bandwidth' : inst.query("CH1:BANDWIDTH?"),
                        'probe' : inst.query("CH1:PRObe?"),
                        'wave' : inst.query_binary_values('CURVe?', datatype='b', is_big_endian=True) 
                    }

                    sample_data['pos' + str(pos_pin) + '_neg' + str(neg_pin) + '_test' + str(test_pin)] = wave_data
                    #plt.plot(wave_data['wave'])
                    #plt.show()

        data.append(sample_data)

    with open('data.json', 'w') as f:
        json.dump(data, f)
                
except KeyboardInterrupt:
    with open('data.json', 'w') as f:
        json.dump(data, f)
        print("data have been saved")



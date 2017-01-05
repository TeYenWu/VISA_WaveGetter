import visa
import numpy as np
from scipy import spatial
import time
import sys
import json
import os

rm = visa.ResourceManager()
rm.list_resources()
inst = rm.open_resource('TCPIP::10.0.1.52::INSTR')
inst.write('DATA:SOURCE CH1')
print(inst.query("*IDN?"))

inst.write('HORizontal:RECOrdlength 20000');
inst.write('DATa:STARt 1');
inst.write('DATa:STOP 20000');

element = raw_input('Enter element name:\n')
filepath = os.path.join(os.getcwd(), element)
if not os.path.exists(filepath):
    os.mkdir(filepath)

spec = raw_input('Enter specification:\n')
filepath = os.path.join(filepath, spec)
if not os.path.exists(filepath):
    os.mkdir(filepath)

os.chdir(filepath)

#filename = 'wave.json'
sample_num = int(raw_input('Enter sample number:\n'))

try:
    #data structure: [{'pos': {'wave': [wave data ...], 'rate': sample rate}, 'neg': {'wave': [wave data ...], 'rate': sample rate}}]


    first = []
    second = []
    for i in range(sample_num):
        while raw_input('Enter Y to gather positive first pin...'):
            pass
        #inst.write('DATA:SOURCE CH1')
        pos = {
            'rate' : float(inst.query('HORizontal:SAMPLERate?')),
            'volt' : float(inst.query('CH1:VOLts?')),
            'pos' : inst.query("CH1:POSition?"),
            'offset' : inst.query("CH1:OFFSet?"),
            'deskew' : inst.query("CH1:DESKew?"),
            'bandwidth' : inst.query("CH1:BANDWIDTH?"),
            'probe' : inst.query("CH1:PRObe?"),
            'wave' : inst.query_binary_values('CURVe?', datatype='b', is_big_endian=True)
        }
        

        #inst.write('DATA:SOURCE CH2')
        while raw_input('Enter Y to gather negative first pin...'):
            pass
        neg = {
            'rate' : inst.query('HORizontal:SAMPLERate?'),
            'volt' : inst.query('CH1:VOLts?'),
            'pos' : inst.query("CH1:POSition?"),
            'offset' : inst.query("CH1:OFFSet?"),
            'deskew' : inst.query("CH1:DESKew?"),
            'bandwidth' : inst.query("CH1:BANDWIDTH?"),
            'probe' : inst.query("CH1:PRObe?"),
            'wave' : inst.query_binary_values('CURVe?', datatype='b', is_big_endian=True)
        }

        first.append({'pos': pos, 'neg': neg})

        while raw_input('Enter Y to gather positive second pin...'):
            pass
        #inst.write('DATA:SOURCE CH1')
        pos = {
            'rate' : inst.query('HORizontal:SAMPLERate?'),
            'volt' : inst.query('CH1:VOLts?'),
            'pos' : inst.query("CH1:POSition?"),
            'offset' : inst.query("CH1:OFFSet?"),
            'deskew' : inst.query("CH1:DESKew?"),
            'bandwidth' : inst.query("CH1:BANDWIDTH?"),
            'probe' : inst.query("CH1:PRObe?"),
            'wave' : inst.query_binary_values('CURVe?', datatype='b', is_big_endian=True)
        }

        #inst.write('DATA:SOURCE CH2')
        while raw_input('Enter Y to gather negative second pin...'):
            pass
        neg = {
            'rate' : inst.query('HORizontal:SAMPLERate?'),
            'volt' : inst.query('CH1:VOLts?'),
            'pos' : inst.query("CH1:POSition?"),
            'offset' : inst.query("CH1:OFFSet?"),
            'deskew' : inst.query("CH1:DESKew?"),
            'bandwidth' : inst.query("CH1:BANDWIDTH?"),
            'probe' : inst.query("CH1:PRObe?"),
            'wave' : inst.query_binary_values('CURVe?', datatype='b', is_big_endian=True)
        }
        second.append({'pos': pos, 'neg': neg})
        #print(valuesi)
        print second
    
    with open('first_pin.json', 'w') as f:
        print(first)
        json.dump(first, f)

    with open('second_pin.json', 'w') as f:
        print(second)
        json.dump(second, f)

except KeyboardInterrupt:
    pass


# #print values
# #values = []
# while True:
#     X = inst.query_binary_values('CURVe?', datatype='b', is_big_endian=True)
#     print 'type to continue.....'
#     sys.stdin.readline()
#     Y = inst.query_binary_values('CURVe?', datatype='b', is_big_endian=True)
#     sim = 1 - spatial.distance.cosine(X,Y)
#     print sim



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

element = input('Enter element name:\n')
filepath = os.path.join(os.getcwd(), element)
if not os.path.exists(filepath):
    os.mkdir(filepath)

spec = input('Enter specification:\n')
filepath = os.path.join(filepath, spec)
if not os.path.exists(filepath):
    os.mkdir(filepath)

os.chdir(filepath)

#filename = 'wave.json'
sample_num = int(input('Enter sample number:\n'))


try:
    #data structure: [{'pos': {'wave': [wave data ...], 'rate': sample rate}, 'neg': {'wave': [wave data ...], 'rate': sample rate}}]


    first = []
    second = []
    for i in range(sample_num):
        while input('Enter Y to gather positive first pin...') != 'Y':
            pass
        #inst.write('DATA:SOURCE CH1')
        pos_rate = inst.query('HORizontal:SAMPLERate?')
        pos_first = inst.query_binary_values('CURVe?', datatype='b', is_big_endian=True)
        
        #inst.write('DATA:SOURCE CH2')
        while input('Enter Y to gather negative first pin...') != 'Y':
            pass
        neg_rate = inst.query('HORizontal:SAMPLERate?')
        neg_first = inst.query_binary_values('CURVe?', datatype='b', is_big_endian=True)
        
        first.append({'pos':{'wave': pos_first, 'rate': pos_rate}, 'neg':{'wave': neg_first, 'rate': neg_rate}})

        while input('Enter Y to gather positive second pin...') != 'Y':
            pass
        #inst.write('DATA:SOURCE CH1')
        pos_rate = inst.query('HORizontal:SAMPLERate?')
        pos_second = inst.query_binary_values('CURVe?', datatype='b', is_big_endian=True)

        #inst.write('DATA:SOURCE CH2')
        while input('Enter Y to gather negative second pin...') != 'Y':
            pass
        neg_rate = inst.query('HORizontal:SAMPLERate?')
        neg_second = inst.query_binary_values('CURVe?', datatype='b', is_big_endian=True)
        second.append({'pos':{'wave': pos_second, 'rate': pos_rate}, 'neg':{'wave': neg_second, 'rate': neg_rate}})
        #print(valuesi)
    
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



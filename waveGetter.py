import visa
import numpy as np
from scipy import spatial
import time
import sys

rm = visa.ResourceManager()
rm.list_resources()
inst = rm.open_resource('TCPIP::10.0.1.52::INSTR')
print(inst.query("*IDN?"))

try:
    while True:
        name = raw_input('FileName:\n')
        values = inst.query_binary_values('CURVe?', datatype='b', is_big_endian=True)
        with open(name, 'w') as f:
            f.write(values)

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



import serial
import sys
import serial.tools.list_ports
import struct
import json
import matplotlib.pyplot as plt
import time

from util import from_bytes
#import circuitTester as ct

def main(argv):
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        print p
    s = serial.Serial("/dev/cu.SLAB_USBtoUART", 115200, parity=serial.PARITY_EVEN)
    print ('bytesize:' + str(s.bytesize))
    s.flushInput()
    s.flushOutput()
    waves = []
    # 0x11 -> control mux (0x02 output wave to target row, 0x03 connect ground to target row, 0x01 connect adc to target row)
    # 0x23 -> read wave (40000byte, 2 byte is int_16)
    # s.write([0x11, 0x02, 0x01, 0x01])
    # print (s.read())
    # s.write([0x23])
    # v = from_bytes(s.read(size=2))
    # Vvalue = float((v-2048)*0.00244140625)
    try:
        # print(s.readline())
        sum_value = 0;
        
        pin_list = [0, 8]
        for i in pin_list:
            s.write([0x11, 0x01, chr(i)])
            result = s.read(size=2)
            for j in pin_list:
                if i == j:
                    continue
                s.write([0x11, 0x02, chr(j)])
                result = s.read(size=2)
                for k in pin_list:
                    print('%d, %d, %d' % (i, j, k))
                    if j == k: 
                        continue
                    s.write([0x11, 0x00, chr(k)])
                    result = s.read(size=2)
                    s.flushInput()
                    s.flushOutput()
                    wave = []
                    for count in range(1):
                        s.write([0x23])
                    
                        for byte_n in xrange(2000):
                            #print('in_waiting:' + str(s.in_waiting))
                            data = s.read(size=2)
                            v = from_bytes(data)
                            Vvalue = float((v-2048)*0.00244140625)                          
                            wave.append(Vvalue)
                            #print(byte_n)

                    data = {
                        'wave': wave,
                        'rate': 80000,
                        'volt': 1,
                    }
                    

                    plt.plot(wave)
                    plt.show()
                    print(ct.two_pin_discriminator(data))
                    print(ct.caculate_C(125, data, 1))
                    
                    #plt.plot(wave)

                    # plt.ylabel('some numbers')
                    # plt.show()
                    #plt.show()
                    # print wave
                    waves.append(wave)


        with open("result.json", 'wb') as output:
            output.write(json.dumps(waves, indent=4))
    #     # print(((num-2048)*0.00244140625))
    #     # data = s.read(size=2)
    #     # result=struct.pack('>h', data)
    #     # print(s.read(size=2))
    #     print ('sum' + str(sum_value/100))
    #     s.close()
    except Exception as e:
        print e
        pass

    
   

if __name__ == "__main__":
    main(sys.argv) 

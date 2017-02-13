import serial
import sys
import serial.tools.list_ports
import struct
import json


def main(argv):
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        print p
    s = serial.Serial("/dev/cu.usbserial", 115200, timeout=10, write_timeout=0)
    waves = []
    # 0x11 -> control mux (0x02 output wave to target row, 0x03 connect ground to target row, 0x01 connect adc to target row)
    # 0x23 -> read wave (40000byte, 2 byte is int_16)
    try:
        # print(s.readline())
        sum_value = 0;

        for i in xrange(6):
            s.write([0x11, 0x02, chr(i)])
            result = s.read(size=1)
            if result != 1:
                break;
            for j in xrange(6):
                if result != 1:
                break;
                s.write([0x11, 0x03, chr(j)])
                result = s.read(size=1)
                for k in xrange(6):
                    if result != 1:
                    break;
                    s.write([0x11, 0x01, chr(k)])
                    result = s.read(size=1)
                    s.write([0x0023])
                    waves.append(s.read(size=40000))



        with open("result.json", 'wb') as output:
            output.write(json.dumps(res, indent=4))
        # print(((num-2048)*0.00244140625))
        # data = s.read(size=2)
        # result=struct.pack('>h', data)
        # print(s.read(size=2))
        print ('sum' + str(sum_value/100))
        s.close()
    except Exception as e:
        print e
        pass
   
def from_bytes (data, big_endian = False):
    if isinstance(data, str):
        data = bytearray(data)
    if big_endian:
        data = reversed(data)   
    num = 0
    for offset, byte in enumerate(data):
        num += byte << (offset * 8)
    return num

if __name__ == "__main__":
    main(sys.argv) 

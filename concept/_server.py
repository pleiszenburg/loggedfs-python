
import random
import pickle
import struct
import sys
import time

PREFIX = b'\xBA\xDE\xAF\xFE'

def send(data):
    data_bin = pickle.dumps(data)
    data_len = struct.pack('Q', len(data_bin)) # Q: uint64
    sys.stdout.buffer.write(PREFIX)
    sys.stdout.buffer.write(data_len)
    sys.stdout.buffer.write(data_bin)
    sys.stdout.flush()

def main():
    count = 0
    while True:
        if count != 3:
            data = {str(item): random.randint(0, 100) for item in range(10)}
        else:
            data = None
        send(data)
        count += 1
        if count == 7:
            raise TypeError('wtf')
        time.sleep(0.5)

if __name__ == '__main__':
    main()

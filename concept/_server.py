
import random
import pickle
import struct
import sys
import time

def send(data):
    data_bin = pickle.dumps(data)
    data_len = struct.pack('Q', len(data_bin)) # Q: uint64
    sys.stdout.buffer.write(data_len)
    sys.stdout.buffer.write(data_bin)
    sys.stdout.flush()

def main():
    while True:
        data = {str(item): random.randint(0, 100) for item in range(10)}
        send(data)
        time.sleep(0.5)

if __name__ == '__main__':
    main()

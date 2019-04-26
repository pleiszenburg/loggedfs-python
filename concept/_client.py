
import pickle
import queue
import struct
import subprocess
import threading
import time

class receiver_class:

    def __init__(self, in_stream, processing_func):
        self._s = in_stream
        self._f = processing_func
        self._q = queue.Queue()
        self._t = threading.Thread(target = receiver_class._worker, args = (self._s, self._q))
        self._t.daemon = True
        self._t.start()

    def flush(self):
        while not self._q.empty():
            try:
                data = self._q.get_nowait()
            except queue.Empty:
                pass
            else:
                self._f(data)
                self._q.task_done()

    @staticmethod
    def _worker(_s, _q):
        while True:
            data_len_encoded = _s.read(8)
            if len(data_len_encoded) != 8: # end of pipe
                break
            data_len = struct.unpack('Q', data_len_encoded)[0] # Q: uint64
            data_bin = _s.read(data_len)
            _q.put(pickle.loads(data_bin))

class manager_class:

    def __init__(self, cmd_list):
        self._proc = subprocess.Popen(
            cmd_list, stdout = subprocess.PIPE, stderr = subprocess.PIPE
            )
        self._proc_alive = True
        self._out_r = receiver_class(self._proc.stdout, print)
        self._err_r = receiver_class(self._proc.stderr, print)
        self._receive()

    def _receive(self):
        while self._proc_alive:
            time.sleep(0.1)
            self._out_r.flush()
            self._err_r.flush()
            self._proc_alive = self._proc.poll() is None
        print('proc died')

def main():
    manager = manager_class(['python3', '_server.py'])

if __name__ == '__main__':
    main()

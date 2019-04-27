
import pickle
import queue
import struct
from subprocess import Popen, PIPE
import threading
import time

PREFIX = b'\xBA\xDE\xAF\xFE'
EOT = -1

class receiver_class:

    def __init__(self, in_stream, decoder_func, processing_func):
        self._s = in_stream
        self._f = processing_func
        self._q = queue.Queue()
        self._t = threading.Thread(target = decoder_func, args = (self._s, self._q))
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

def _out_decoder(_s, _q):
    prefix_len = len(PREFIX)
    while True:
        prefix = _s.read(prefix_len)
        if len(prefix) == 0: # end of pipe
            _q.put(EOT * 10)
            break
        data_len_encoded = _s.read(8)
        data_len = struct.unpack('Q', data_len_encoded)[0] # Q: uint64
        data_bin = _s.read(data_len)
        _q.put(pickle.loads(data_bin))

def _err_decoder(_s, _q):
    while True:
        msg = _s.readline()
        if len(msg) == 0:
            _q.put(EOT * 100)
            break
        _q.put(msg.decode('utf-8'))

class manager_class:

    def __init__(self, cmd_list, out_func, err_func, exit_func):
        self._exit_func = exit_func
        self._proc = Popen(cmd_list, stdout = PIPE, stderr = PIPE)
        self._proc_alive = True
        self._out_r = receiver_class(self._proc.stdout, _out_decoder, out_func)
        self._err_r = receiver_class(self._proc.stderr, _err_decoder, err_func)
        self._receive()

    def _receive(self):
        while self._proc_alive:
            time.sleep(0.1) # TODO good interval?
            self._out_r.flush()
            self._err_r.flush()
            self._proc_alive = self._proc.poll() is None
        self._exit_func()

def main():
    manager = manager_class(
        ['python3', '_server.py'],
        demo_consumer_out,
        demo_consumer_err,
        demo_exit
        )

def demo_consumer_out(msg):
    print('OUT: ', msg)

def demo_consumer_err(msg):
    if isinstance(msg, str):
        print('ERR: ', msg[:-1])
    else:
        print('ERR: ', msg)

def demo_exit():
    print('Proc died!')

if __name__ == '__main__':
    main()

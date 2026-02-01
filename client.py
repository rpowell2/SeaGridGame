import sys
import time
import struct
import threading
import socket

class client:
    def __init__(self, host='127.0.0.1', port=62743):
        self.host = host
        self.port = port

        self.kill = False

        self.socket = None

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
            s.connect((self.host, self.port))
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
            s.settimeout(1)
            print('connected',s)
            self.socket = s
            while not self.kill:
                try:
                    data = self.socket.recv(4096)
                    if len(data):
                        self.deserialize(data)
                except socket.timeout:
                    pass
                time.sleep(0.001)
client()


import socket

class VPNServerConnection(object):
    def __init__(self, host=None, port=None):
        (self.host, self.port) = (host, port)
        self.connect()
    
    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.sock.setblocking(0)
    
    def read(self):
        pass
    
    def write(self):
        pass

    def close(self):
        self.sock.close()
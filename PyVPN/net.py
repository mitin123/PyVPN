import struct
from gevent import socket
from packet import Packet

class VPNServerConnection(object):
    def __init__(self, host=None, port=None):
        (self.host, self.port) = (host, port)
        self.connect()
    
    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def read_packet(self):
        print "read net"
        size = struct.unpack("H", self.sock.recv(2))[0]
        data = self.sock.recv(size)
        return Packet(data, size)

    def write_packet(self, packet):
        print "write net"
        #self.sock.send(struct.pack("H", packet.size))
        self.sock.send(packet.data)
        print "write net end"
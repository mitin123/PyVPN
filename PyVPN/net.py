import struct
from gevent import socket
from packet import Packet

class VPNConnection(object):
    def read_packet(self):
        print "read net"
        size = struct.unpack("H", self.sock.recv(2))[0]
        src = struct.unpack("i", self.sock.recv(4))[0]
        dst = struct.unpack("i", self.sock.recv(4))[0]
        data = self.sock.recv(size)
        return Packet(data, size=size, src=src, dst=dst)

    def write_packet(self, packet):
        print "write net"
        self.sock.send(struct.pack("H", packet.size))
        self.sock.send(struct.pack("i", packet.src))
        self.sock.send(struct.pack("i", packet.dst))
        self.sock.send(packet.data)
        print "write net end"

class VPNServerConnection(VPNConnection):
    def __init__(self, host=None, port=None):
        (self.host, self.port) = (host, port)
        self.connect()

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

class VPNClientConnection(VPNConnection):
    def __init__(self, sock):
        self.sock = sock

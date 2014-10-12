import struct
from gevent import socket
from packet import Packet

class VPNConnection(object):
    def read_packet(self):
        size, src, dst = struct.unpack("Hii", self.sock.recv(struct.calcsize("Hii")))
        data = self.sock.recv(size)
        packet = Packet(data, size=size, src=src, dst=dst)
        print "read from net %s" % packet
        return packet

    def write_packet(self, packet):
        self.sock.send(struct.pack("Hii", packet.size, packet.src, packet.dst))
        self.sock.send(packet.data)
        print "write to net %s" % packet

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

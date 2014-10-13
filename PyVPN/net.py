import struct
from gevent import socket
from packet import Packet

class VPNConnection(object):
    def read_packet(self):
        packet = Packet.read_from_socket(self.sock)
        print "read from net %s" % packet
        return packet

    def write_packet(self, packet):
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

import struct
from gevent import socket
from packet import Packet

from crypto import crypto_pool

class VPNConnection(object):
    def __init__(self, crypto=None, auth=None):
        raise NotImplementedError()

    def read_packet(self):
        packet = Packet.read_from_socket(self.sock)
        print "read from net %s" % packet
        return self.decrypt_packet(packet)

    def write_packet(self, packet):
        encrypted_packet = self.encrypt_packet(packet)
        self.sock.send(encrypted_packet.data)
        print "write to net %s" % packet

    def encrypt_packet(self, packet):
        packet.data = self.crypto.encrypt(packet.data)
        return packet

    def decrypt_packet(self, packet):
        packet.data = self.crypto.decrypt(packet.data)
        return packet

# connection with server
class VPNServerConnection(VPNConnection):
    def __init__(self, host=None, port=None, config=None):
        self.host, self.port = host, port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

        self.sock.send(socket.inet_pton(socket.AF_INET, config.ip))
        self.sock.send(struct.puck("HH", [config.auth_no, config.crypto_no]))

# connection with client
class VPNClientConnection(VPNConnection):
    def __init__(self, sock):
        self.sock = sock
        self.ip, self.auth_no, self.crypto_no = struct.unpack("iHH", self.sock.recv(8))

        self.crypto = crypto_pool.get(self.crypto_no)

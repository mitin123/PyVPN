from _socket import inet_pton, inet_ntoa

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
    def __init__(self, host=None, port=None, app=None):
        self.host, self.port, self.app = host, port, app

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

        if "ip" not in self.app.config:
            self.app.config["ip"] = "0.0.0.0" # server allocate address from pull (like simple dummy DHCP)

        self.make_handshake()

    def make_handshake(self):
        self.sock.send(socket.inet_pton(socket.AF_INET, self.app.config.ip))
        self.sock.send(struct.pack("HH", self.app.config.auth_no, self.app.config.crypto_no))

        self.crypto_no = self.app.config.crypto_no
        self.crypto = crypto_pool.get(self.app.config.crypto_no)

        self.app.config["ip"] = inet_ntoa(self.sock.recv(4)) # ip

# connection with client
class VPNClientConnection(VPNConnection):
    def __init__(self, sock):
        self.sock = sock

        self.make_handshake()

    def make_handshake(self):
        data = self.sock.recv(8)
        if len(data) < 8:
            data += self.sock.recv(8 - len(data))
        self.ip, self.auth_no, self.crypto_no = struct.unpack("iHH", data)

        if self.ip == 0:
            self.ip = inet_pton("10.0.0.17") # !!! allocate address

        self.sock.send(struct.pack("i", self.ip))

        self.crypto = crypto_pool.get(self.crypto_no)


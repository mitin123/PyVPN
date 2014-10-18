from socket import inet_pton, inet_ntoa

import struct
from gevent import socket
from packet import Packet
from vpnexcept import VPNException


class VPNConnection(object):
    def __init__(self):
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
        packet.data = self.app.crypto.encrypt(packet.data)
        return packet

    def decrypt_packet(self, packet):
        packet.data = self.crypto.decrypt(packet.data)
        return packet

    def _readn(self, n):
        data = self.sock.recv(n)
        while len(data) < n:
            data += self.sock.recv(n - len(data))
        return data

    def _write(self,data):
        self.sock.send(data)

# connection with server
class VPNServerConnection(VPNConnection):
    def __init__(self, host=None, port=None, app=None):
        self.host, self.port, self.app = host, port, app
        self.logger = self.app.logger

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

        if "ip" not in self.app.config:
            self.app.config["ip"] = "0.0.0.0" # server allocate address from pull (like simple dummy DHCP)

        self.make_handshake()

    def make_handshake(self):
        self.auth_no = struct.unpack("=H", self._readn(2))[0] # RECEIVE AUTH_NO

        auth = self.app.auth_pool.get(self.auth_no)
        if auth is None:
            raise VPNException("auth method %s not registered in auth_pool" % self.auth_no)
        try:
            auth.client_side_auth(self.sock) # make auth
        except:
            raise VPNException("Authentication failed (auth=%s)" % auth._index)

        ip = socket.inet_pton(socket.AF_INET, self.app.config.ip)
        # send ip, crypto
        self._write(ip)
        self._write(struct.pack("=H",self.app.config.crypto_no))

        self.app.config["ip"] = inet_ntoa(self._readn(4)) # recv real ip

# connection with client
class VPNClientConnection(VPNConnection):
    def __init__(self, sock, app):
        self.sock = sock
        self.app = app
        self.logger = self.app.logger

        self.make_handshake()

    def make_handshake(self):
        self._write(struct.pack("=H", self.app.config.auth_no)) # SEND AUTH_NO

        self.logger.info("start auth for %s by auth_type=%s" % (self.sock, self.app.auth._index))
        if not self.app.auth.server_side_auth(self.sock): # make auth
            raise VPNException("failed auth for %s by auth_type=%s" % (self.sock, self.app.auth._index))
        self.logger.info("successful auth for %s by auth_type=%s" % (self.sock, self.app.auth._index))

        self.ip, self.crypto_no = struct.unpack("=iH", self._readn(6)) # recv ip, crypto

        self.crypto = self.app.crypto_pool.get(self.crypto_no)

        if self.ip == 0:
            self.ip = inet_pton(socket.AF_INET, "10.0.0.17") # !!! allocate address
        else:
            self.ip = struct.pack("i", self.ip)

        self._write(self.ip) # send real ip
        self.logger.info("ip address %s was assigned to client %s" % (inet_ntoa(self.ip), self.sock))

from socket import inet_pton, inet_ntoa

import struct
import time
from gevent import socket
from packet import Packet
from crypto import crypto_pool
from auth import auth_pool
from key_exchange import DiffieHellman
from vpnexcept import VPNException

CONTENT_TYPES = {
    "packet_data": 1,
    "update_session": 2
}

class VPNConnection(object):
    def __init__(self):
        self.key_exchange_protocol = DiffieHellman(self.sock)

    def make_handshake(self):
        raise NotImplementedError

    def read_packet(self):
        type = struct.unpack("i", self._readn(4))[0]
        if type == CONTENT_TYPES["packet_data"]:
            packet_len = struct.unpack("i", self._readn(4))[0]
            packet = Packet.read_from_socket(self, packet_len, decrypt_func=self.crypto.decrypt)
            print "read from net %s" % packet
            return packet
        elif type == CONTENT_TYPES["update_session"]:
            self.update_session_key()
            return self.read_packet()

    def write_packet(self, packet):
        packet.encrypt(self.crypto.encrypt)
        self._write(struct.pack("i", CONTENT_TYPES["packet_data"])) # send packet type
        self._write(struct.pack("i", len(packet.data))) # send packet size
        packet.write_to_socket(self.sock)
        print "write to net %s" % packet

    def _readn(self, n):
        data = self.sock.recv(n)
        while len(data) < n:
            data += self.sock.recv(n - len(data))
        return data

    def _write(self,data):
        self.sock.sendall(data)

    def close(self):
        self.sock.close()

    def is_alive(self):
        return True

# connection with server
class VPNServerConnection(VPNConnection):
    def __init__(self, host=None, port=None, app=None):
        self.host, self.port, self.app = host, port, app
        self.logger = self.app.logger

        self.crypto = crypto_pool.alloc(self.app.config.crypto_no)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

        if "ip" not in self.app.config:
            self.app.config["ip"] = "0.0.0.0" # server allocate address from pull (like simple dummy DHCP)

        super(VPNServerConnection, self).__init__()

        self.make_handshake()

    def make_handshake(self):
        self.auth_no = struct.unpack("=H", self._readn(2))[0] # RECEIVE AUTH_NO

        auth = auth_pool.alloc(self.auth_no)

        try:
            auth.client_side(self.sock) # make auth
        except:
            raise VPNException("Authentication failed (auth=%s)" % auth._index)

        ip = socket.inet_pton(socket.AF_INET, self.app.config.ip)
        # send ip, crypto
        self._write(ip)
        self._write(struct.pack("=H", self.app.config.crypto_no))

        self.app.config["ip"] = inet_ntoa(self._readn(4)) # recv real ip

    def update_session_key(self):
        self.session_key = self.key_exchange_protocol.client_side()
        #print "new session key", self.session_key


# connection with client
class VPNClientConnection(VPNConnection):
    def __init__(self, sock, app):

        self.sock = sock
        self.app = app
        self.logger = self.app.logger

        self.auth = auth_pool.alloc(self.app.config.auth_no)

        super(VPNClientConnection, self).__init__()

        self.make_handshake()

        self.update_session_key()

    def make_handshake(self):
        self._write(struct.pack("=H", self.app.config.auth_no)) # SEND AUTH_NO

        self.logger.info("start auth for %s by auth_type=%s" % (self.sock, self.auth._index))

        if not self.auth.server_side(self.sock): # make auth
            raise VPNException("failed auth for %s by auth_type=%s" % (self.sock, self.auth._index))
        self.logger.info("successful auth for %s by auth_type=%s" % (self.sock, self.auth._index))

        self.ip, self.crypto_no = struct.unpack("4sH", self._readn(6))

        self.crypto = crypto_pool.alloc(self.crypto_no)

        if self.ip == '\x00\x00\x00\x00':
            self.ip = inet_pton(socket.AF_INET, "10.0.0.17") # !!! allocate address
        elif self.ip in self.app.connections and self.app.connections[self.ip].is_alive():
            ip_str = ".".join([str(ord(i)) for i in self.ip])
            # raise VPNException("ip address %s already allocated" % ip_str)

        if self.crypto is None:
            raise VPNException("crypto with index %s not found" % self.crypto_no)

        self._write(self.ip) # send real ip
        self.logger.info("ip address %s was assigned to client %s" % (inet_ntoa(self.ip), self.sock))

    def update_session_key(self):
        self._write(struct.pack("i", CONTENT_TYPES["update_session"]))
        self.session_key = self.key_exchange_protocol.server_side()
        #print "new session key", self.session_key
        self.last_update_session_key_time = time.time()

    def session_has_expired(self):
        expiry_time = self.last_update_session_key_time + self.key_exchange_protocol.get_session_period()
        return time.time() > expiry_time


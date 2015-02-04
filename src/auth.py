#-*- coding: utf8 -*-

from crypto_protocol import CryptoProtocol
from utils import AbstractPool
from vpnexcept import VPNException

class AuthPool(AbstractPool):

    def not_found(self, index):
        raise VPNException("auth method %s not registered in auth_pool" % index)

class Auth(CryptoProtocol):

    def __init__(self):
        # TUDO: must be initialized
        self.public_key = None
        self.private_key = None
        if hasattr(self, "init"):
            self.init()

    def client_side(self, sock):
        raise NotImplementedError()

    def server_side(self, sock):
        raise NotImplementedError()

class NoAuth(Auth):

    _index = 1

    def client_side(self, sock):
        pass

    def server_side(self, sock):
        return True

import struct
# return true, if client send value 42
class DummyAuth(Auth):

    _index = 2

    def client_side(self, sock):
        sock.send(struct.pack("=H", 42))

    def server_side(self, sock):
        res = struct.unpack("=H", sock.recv(struct.calcsize("=H")))[0]
        return res == 42


auth_pool = AuthPool()

auth_pool.register(NoAuth)
auth_pool.register(DummyAuth)

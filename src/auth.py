#-*- coding: utf8 -*-

from vpnexcept import VPNException

class AuthPool(object):
    def __init__(self):
        self.__classes = {}

    def register(self, auth_cls):
        if hasattr(auth_cls, "_index"):
            self.__classes[auth_cls._index] = auth_cls

    def alloc(self, index):
        if index not in self.__classes:
            raise VPNException("auth method %s not registered in auth_pool" % index)

        return self.__classes[index]()

class Auth(object):
    def client_side_auth(self, sock):
        raise NotImplementedError()

    def server_side_auth(self, sock):
        raise NotImplementedError()

class NoAuth(Auth):
    _index = 1

    def client_side_auth(self, sock):
        pass

    def server_side_auth(self, sock):
        return True

import struct
# return true, if client send value 42
class DummyAuth(Auth):
    _index = 2

    def client_side_auth(self, sock):
        sock.send(struct.pack("=H", 42))

    def server_side_auth(self, sock):
        res = struct.unpack("=H", sock.recv(struct.calcsize("=H")))[0]
        return res == 42

auth_pool = AuthPool()

auth_pool.register(NoAuth)
auth_pool.register(DummyAuth)

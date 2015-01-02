#-*- coding: utf8 -*-

__author__ = 'amitin'

class AuthPool(object):
    def __init__(self, app):
        self.app = app
        self.logger = app.logger
        self.__classes = {}

        self.register(NoAuth)
        self.register(DummyAuth)

    def register(self, auth_cls):
        if hasattr(auth_cls, "_index"):
            self.__classes[auth_cls._index] = auth_cls

    def get(self, index):
        return self.__classes[index](app=self.app)

class Auth(object):
    def __init__(self, app=None):
        self.app = app

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

#-*- coding: utf8 -*-

from utils import AbstractPool
from vpnexcept import VPNException

class CryptoPool(AbstractPool):
    def not_found(self, index):
        raise VPNException("crypto method %s not registered in crypto_pool" % index)


class Crypto(object):
    def __init__(self, key=None):
        self.key = key

    def set_key(self, key):
        self.key = key

    def encrypt(self, data):
        raise NotImplementedError()

    def decrypt(self, data):
        raise NotImplementedError()


class NoCrypto(Crypto):
    _index = 1

    def encrypt(self, data):
        return data

    def decrypt(self, data):
        return data


class DummyCrypto(Crypto):
    _index = 2

    def encrypt(self, data):
        return "".join(map(lambda x: chr(ord(x)^42), data))

    decrypt = encrypt


crypto_pool = CryptoPool()

crypto_pool.register(NoCrypto)
crypto_pool.register(DummyCrypto)
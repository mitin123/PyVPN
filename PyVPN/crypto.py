#-*- coding: utf8 -*-

__author__ = 'amitin'

class CryptoPool(object):
    def __init__(self):
        self.__classes = {}
        self.__pool = {}

    def register(self, crypto_cls):
        self.__classes[crypto_cls._index] = crypto_cls

    def get(self, index):
        if index in self.__classes:
            new = self.__classes[index].__new__()
            if index not in self.__pool:
                self.__pool[index] = []
            self.__pool.append(new)

        return new

class Crypto(object):
    def __init__(self, context):
        self.context = context

    def encrypt(self, data):
        raise NotImplementedError()

    def decrypt(self):
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


# заполняем пул из всех возможых мест.
# криптомодулем может быть программа на любом языке,
# т.ч. продумать о возможности предоставлять инетфейс Crypto для этих программ
crypto_pool = CryptoPool()

crypto_pool.register(NoCrypto)
crypto_pool.register(DummyCrypto)
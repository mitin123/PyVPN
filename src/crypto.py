#-*- coding: utf8 -*-

from collections import defaultdict
from vpnexcept import VPNException

class CryptoPool(object):
    def __init__(self):
        self.__classes = {}
        self.__pool = defaultdict(list)

    def register(self, crypto_cls):
        if hasattr(crypto_cls, "_index"):
            self.__classes[crypto_cls._index] = crypto_cls

    def alloc(self, index):
        if index in self.__classes:
            new = self.__classes[index]()
            self.__pool[index].append(new)
            return new
        else:
            raise VPNException("crypto method %s not registered in crypto_pool" % self.auth_no)


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
# заполняем пул криптомодулей из всех возможых мест.
# криптомодуль - объект класса, реализующего интерфейс Crypto
# при регистрации модулю прогнать ряд тестов на работоспособность
# криптомодулем ТАКЖЕ может быть программа на любом языке работающая со стандартным вводом-выводом,
# продумать о возможности предоставлять инетфейс Crypto для этих программ,
# о взаимодействие криптомодуля с Crypto прослойкой, и о передаче параметров (ключ, режим) этой программе.
# также нужно менеджить процессы с запущенными модулями (например собирать статистику
# по зашифрованным/расшифрованным пакетам, расход памяти)
# и убивать процесс при падение сокета
# подумать о поддержке криптомодулей только на python и cython
crypto_pool.register(NoCrypto)
crypto_pool.register(DummyCrypto)
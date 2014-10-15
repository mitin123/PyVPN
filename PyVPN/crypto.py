#-*- coding: utf8 -*-

__author__ = 'amitin'

class CryptoPool(object):
    def __init__(self):
        self.__classes = {}
        self.__pool = {}

    def register(self, crypto_cls):
        if hasattr(crypto_cls, "_index"):
            self.__classes[crypto_cls._index] = crypto_cls

    def get(self, index):
        if index in self.__classes:
            new = self.__classes[index]()
            if index not in self.__pool:
                self.__pool[index] = []
            self.__pool[index].append(new)

        return new

class Crypto(object):
    def __init__(self, context=None):
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


# заполняем пул криптомодулей из всех возможых мест.
# криптомодуль - объект класса, реализующего интерфейс Crypto
# при регистрации модулю прогнать ряд тестов на работоспособность
# криптомодулем ТАКЖЕ может быть программа на любом языке работающая со стандартным вводом-выводом,
# продумать о возможности предоставлять инетфейс Crypto для этих программ,
# о взаимодействие криптомодуля с Crypto прослойкой, и о передаче параметров (ключ, режим) этой программе.
# также нужно менеджить процессы с запущенными модулями (например собирать статистику
# по зашифрованным/расшифрованным пакетам, расход памяти)
# и убивать процесс при падение сокета
crypto_pool = CryptoPool()

crypto_pool.register(NoCrypto)
crypto_pool.register(DummyCrypto)
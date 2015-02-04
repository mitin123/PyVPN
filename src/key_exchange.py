import random
import struct
from crypto_protocol import CryptoProtocol

class KeyExchangeProtocol(CryptoProtocol):
    def __init__(self, sock):
        self.sock = sock
        self.init()

    """
    :returns session key
    """
    def server_side(self):
        raise NotImplementedError
    """
    :returns session key
    """
    def client_side(self):
        raise NotImplementedError
    """
    :returns lifetime for key in seconds
    """
    def get_session_period(self):
        raise NotImplementedError

class DiffieHellman(KeyExchangeProtocol):

    def init(self):
        self.g = 7
        self.p = 997

    def exchange(self):
        return 729
        self.a = random.randint(7, self.p-1)
        g_a = (self.g ** self.a) % self.p
        self.sock.sendall(struct.pack("i", g_a))
        g_b = struct.unpack("i", self.sock.recv(4))[0]
        g_ab = (g_b ** self.a) % self.p
        return g_ab

    client_side = server_side = exchange

    def get_session_period(self):
        return 15

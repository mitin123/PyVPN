class CryptoProtocol(object):

    def __init__(self):
        pass

    def client_side(self, sock):
        raise NotImplementedError

    def server_side(self, sock):
        raise NotImplementedError
import struct
from gevent.socket import inet_ntop, AF_INET

class Packet(object):
    def __init__(self, data, size=None, dst=None):
        self.data = data
        self.size = size
        self.dst= dst

    def dst_asstring(self):
        return inet_ntop(AF_INET, struct.pack("i", self.dst))
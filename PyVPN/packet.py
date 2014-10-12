import struct
from gevent.socket import inet_ntop, AF_INET

class Packet(object):
    def __init__(self, data, size=None, src=None, dst=None):
        self.data = data
        self.size = size
        self.src= src
        self.dst= dst

    def dst_asstring(self):
        return inet_ntop(AF_INET, struct.pack("i", self.dst))

    def src_asstring(self):
        return inet_ntop(AF_INET, struct.pack("i", self.src))

    def __repr__(self):
        return "(size=%s src=%s dst=%s)" % (self.size, self.src_asstring(), self.dst_asstring())
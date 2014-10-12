import struct
from gevent.socket import inet_ntop, AF_INET, ntohs

class Packet(object):
    def __init__(self, data, header=None):
        self.data = data
        self.header = header

    def dst_asstring(self):
        return inet_ntop(AF_INET, struct.pack("i", self.header["dst"]))

    def src_asstring(self):
        return inet_ntop(AF_INET, struct.pack("i", self.header["src"]))

    def __repr__(self):
        return repr(self.header)

    @staticmethod
    def read_from_socket(socket, header_safe=False):
        ip_header_format = "!HHHHHHii"
        ip_header_size = struct.calcsize(ip_header_format)

        raw_header = socket.recv(ip_header_size)

        c1, c2, c3, c4, c5, c6, src, dst = struct.unpack(ip_header_format, raw_header)

        header = {
            "ver" : c1 >> 12,
            "ihl" : (c1 >> 8) & 0b00001111,
            "dscp" : (c1 & 255) >> 3,
            "ecn" : c1 & 3,
            "length" : c2, # length of packet with header in bytes
            "id" : c3,
            "flags" : c4 >> 13,
            "offset" : c4 & 0b1111111111111,
            "ttl" : c5 >> 8,
            "protocol" : c5 & 255,
            "checksum" : c6,
            "src": src,
            "dst" : dst,
        }

        if header["ihl"] > 5:
            socket.recv((header["ihl"]-5)*4)

        data_size = header["length"]-header["ihl"]*4

        data = ""
        if header_safe:
            data += raw_header
        data += socket.recv(data_size)

        return Packet(data, header=header)


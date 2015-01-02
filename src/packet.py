import struct
from gevent.socket import htonl, inet_ntop, AF_INET

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

    IP_HEADER_FORMAT = "!iHHHHHHii"

    @staticmethod
    def __retrieve_ipv4_header(raw_data):

        ip_header_size = struct.calcsize(Packet.IP_HEADER_FORMAT)
        raw_header = raw_data[:ip_header_size]
        trash, c1, c2, c3, c4, c5, c6, src, dst = struct.unpack(Packet.IP_HEADER_FORMAT, raw_header)

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
            "src": htonl(src),
            "dst" : htonl(dst),
        }

        return header

    """
    @staticmethod
    def read_from(dev, *args, **kwargs):
        if isinstance(dev, Tun):
            return Packet.read_from_tun(dev, *args, **kwargs)
        elif isinstance(dev, VPNConnection):
            return Packet.read_from_socket(dev, *args, **kwargs)
    """

    @staticmethod
    def read_from_tun(dev, packet_size=65000):
        raw_data = dev.sock.recv(packet_size)
        header = Packet.__retrieve_ipv4_header(raw_data)
        return Packet(raw_data, header=header)

    @staticmethod
    def read_from_socket(dev):
        raw_header = dev._readn(struct.calcsize(Packet.IP_HEADER_FORMAT))
        header = Packet.__retrieve_ipv4_header(raw_header)
        if header["ihl"] > 5:
            dev._readn((header["ihl"]-5)*4)
        data_size = header["length"]-header["ihl"]*4
        data = raw_header + dev._readn(data_size)

        return Packet(data, header=header)

import struct
from gevent.socket import inet_ntop, AF_INET, ntohs

class Packet(object):
    def __init__(self, data, header=None):
        self.header = header


        """
        trash, c1, c2, c3, c4, c5, c6, src, dst = struct.unpack("!iHHHHHHii", data[24:48])
        ver = c1 >> 12
        ihl = (c1 >> 8) & 0b00001111
        dscp = (c1 & 255) >> 3
        ecn = c1 & 3
        id = c3
        flags = c4 >> 13
        offset = c4 & 0b1111111111111
        ttl = c5 >> 8
        protocol = c5 & 255
        checksum = c6

        print ver, ihl, dscp, ecn, id, flags, offset, ttl, protocol, checksum, inet_ntop(AF_INET, struct.pack("!i", src)), inet_ntop(AF_INET, struct.pack("!i", dst))

        """
        
        
        if self.protocol == 6:
            src_port, dst_port, seq, ack, flags, ws = struct.unpack("!HHIIHH", data[48:64])
            print "tcp: src=%s dst=%s seq=%s ack=%s" % (src_port, dst_port, seq, ack)
            print "fin=%s" % (flags&1)
            print "syn=%s" % ((flags>>1)&1)
            print "rst=%s" % ((flags>>2)&1)
            print "psh=%s" % ((flags>>3)&1)
            print "ack=%s" % ((flags>>4)&1)
            print "urg=%s" % ((flags>>5)&1)
            print "offset=%s" % (flags >> 12)


        print struct.unpack("!%sc" % len(data[72:]), data[72:])


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

        c1, c2, c3, c4, c5, c6, src, dst = struct.unpack(ip_header_format, raw_header[0:ip_header_size])

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


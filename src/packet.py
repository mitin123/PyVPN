import struct
from gevent.socket import ntohl, inet_ntop, AF_INET

IP_HEADER_FORMAT = "!iHHHHHH4s4s"
IP_HEADER_SIZE = struct.calcsize(IP_HEADER_FORMAT)


class Packet(object):
    def __init__(self, data, header=None, encrypted=False):
        self.data = data
        self.header = header
        self.encrypted = encrypted

    def dst_asstring(self):
        return inet_ntop(AF_INET, struct.pack("i", self.header["dst"]))

    def src_asstring(self):
        return inet_ntop(AF_INET, struct.pack("i", self.header["src"]))

    def __repr__(self):
        return repr(self.header)

    @staticmethod
    def __retrieve_ipv4_header(raw_data):
        raw_header = raw_data[:IP_HEADER_SIZE]
        trash, c1, c2, c3, c4, c5, c6, src, dst = struct.unpack(IP_HEADER_FORMAT, raw_header)

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

        return header

    def decrypt(self, decrypt_func):
        if self.encrypted:
            self.data = decrypt_func(self.data)
            self.header = Packet.__retrieve_ipv4_header(self.data)
            self.encrypted = False

    def encrypt(self, encrypt_func):
        if not self.encrypted:
            self.data = encrypt_func(self.data)
            self.encrypted = True

    @staticmethod
    def read_from_tun(dev, packet_size=65000):
        raw_data = dev.sock.recv(packet_size)
        header = Packet.__retrieve_ipv4_header(raw_data)
        return Packet(raw_data, header=header)


    @staticmethod
    def read_from_socket(conn, size, decrypt_func=None):
        data = conn._readn(size)
        if decrypt_func is not None:
            data = decrypt_func(data)
        header = Packet.__retrieve_ipv4_header(data)
        return Packet(data, header=header)

    def write_to_socket(self, sock):
        sock.sendall(self.data)
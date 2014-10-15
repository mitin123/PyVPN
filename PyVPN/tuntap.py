import os
import fcntl
import struct

from subprocess import call
from socket import ntohs
from gevent.os import tp_read, tp_write

from vpnexcept import VPNException
from packet import Packet

from adapters import FileToSocketAdapter
from  nonblock import NonblockFileWrapper

class TunTapException(VPNException):
    pass

TUNSETIFF = 0x400454ca
IFF_TUN   = 0x0001
IFF_TAP   = 0x0002

class TunTap(object):
    pass

class Tun(TunTap):
    def __init__(self, name="tun1"):
        self.name = name
        self.sock = self.open() # support socket interface recv and send
    
    def open(self):
        TUNMODE = IFF_TUN
        f = os.open("/dev/net/tun", os.O_RDWR)
        ifs = fcntl.ioctl(f, TUNSETIFF, struct.pack("16sH", self.name, TUNMODE))
        self.ifname = ifs[:16].strip("\x00")
        return FileToSocketAdapter(NonblockFileWrapper(f))

    def configure(self, ip=None, mask=None):
        if ip is not None and mask is not None:
            if call("ip link set %s up" % self.name, shell=True) != 0:
                raise TunTapException("can`t set %s up" % self.name)
            if call("ip addr add %s/%s dev %s" % (ip, mask, self.name), shell=True) != 0:
                raise TunTapException("can`t set subnet for interface %s" % self.name)

    def read_packet(self):
        packet = Packet.read_from_tun(self.sock)
        print "read from tun %s" % packet
        return packet

    def write_packet(self, packet):
        if packet.header["protocol"] == 6:
            src_port, dst_port, seq, ack, flags, ws = struct.unpack("!HHIIHH", packet.data[0:16])
            print "*"*10
            print "tcp: src=%s dst=%s seq=%s ack=%s" % (src_port, dst_port, seq, ack)
            print "fin=%s" % (flags&1)
            print "syn=%s" % ((flags>>1)&1)
            print "rst=%s" % ((flags>>2)&1)
            print "psh=%s" % ((flags>>3)&1)
            print "ack=%s" % ((flags>>4)&1)
            print "urg=%s" % ((flags>>5)&1)
            print "offset=%s" % (flags >> 12)
            print "*"*10
        self.sock.send(packet.data)
        print "write to tun %s" % packet
import os
import fcntl
import struct

from subprocess import call
from socket import ntohs
from gevent.os import tp_read, tp_write

from vpnexcept import VPNException
from packet import Packet

class TunTapException(VPNException):
    pass

TUNSETIFF = 0x400454ca
IFF_TUN   = 0x0001
IFF_TAP   = 0x0002

class TunTap(object):
    pass

class Tun(TunTap):
    def __init__(self, name="tun0"):
        self.name = name
        self.fd = self.open()
    
    def open(self):
        TUNMODE = IFF_TUN
        #f = open("/dev/net/tun", "rw")
        f = os.open("/dev/net/tun", os.O_RDWR)
        #make_nonblocking(f) # make non-block socket, block greenlet only
        ifs = fcntl.ioctl(f, TUNSETIFF, struct.pack("16sH", self.name, TUNMODE))
        self.ifname = ifs[:16].strip("\x00")
        return f

    def configure(self, ip=None, mask=None):
        if ip is not None and mask is not None:
            if call("ip link set %s up" % self.name, shell=True) != 0:
                raise TunTapException("can`t set %s up" % self.name)
            if call("ip addr add %s/%s dev %s" % (ip, mask, self.name), shell=True) != 0:
                raise TunTapException("can`t set subnet for interface %s" % self.name)

    def read_packet(self):
        #res =  struct.unpack("iHHiicccccccc", self.fd.read(24))
        #print ntohs(res[0]), res[0]
        #print ntohs(res[2]), res[2]
        #print map(ord, res[5:])
        #return
        first_32bit = tp_read(self.fd, 24)
        trash, lpart, rpart, f1, f2, src, dst = struct.unpack("iHHiiii", first_32bit)

        size = ntohs(rpart)

        data = struct.pack("iHHiiii", trash, lpart, rpart, f1, f2, src, dst)
        data += tp_read(self.fd, size-20)

        packet = Packet(data, size=size+4, src=src, dst=dst)

        print "read from tun %s" % packet

        return packet

    def write_packet(self, packet):
        tp_write(self.fd, packet.data)
        print "write tun %s" % packet
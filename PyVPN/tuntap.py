import os
import fcntl
import struct

from subprocess import Popen, call
from gevent.socket import wait_readwrite, ntohs

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
        f = open("/dev/net/tun", "rw")
        wait_readwrite(f.fileno()) # make non-block socket, block greenlet only
        ifs = fcntl.ioctl(f, TUNSETIFF, struct.pack("16sH", self.name, TUNMODE))
        self.ifname = ifs[:16].strip("\x00")
        return f

    def configure(self, subnet=None):
        if subnet is not None:
            if call("ip link set %s up" % self.name, shell=True) != 0:
                raise TunTapException("can`t set %s up" % self.name)
            if call("ip addr add %s dev %s" % (subnet, self.name), shell=True) != 0:
                raise TunTapException("can`t set subnet for interface %s" % self.name)

    def read_packet(self):
        #res =  struct.unpack("iHHiicccccccc", self.fd.read(24))
        #print ntohs(res[0]), res[0]
        #print ntohs(res[2]), res[2]
        #print map(ord, res[5:])
        #return
        #print "read tun"
        first_32bit = self.fd.read(8)
        trash, lpart, rpart = struct.unpack("iHH", first_32bit)
        print "read tun end"
        size = ntohs(rpart)
        print rpart
        print size, type(size)
        data = struct.pack("HH", lpart, rpart)
        data += self.fd.read(56)
        print "".join([a for a in data])
        return Packet(data, size)

    def write_packet(self, packet):
        self.fd.write(packet.data)
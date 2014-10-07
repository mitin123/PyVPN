import os
import fcntl
import struct

from subprocess import Popen, call

from vpnexcept import VPNException


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
        MODE = 0
        DEBUG = 0
        f = os.open("/dev/net/tun", os.O_RDWR)
        ifs = fcntl.ioctl(f, TUNSETIFF, struct.pack("16sH", self.name, TUNMODE))
        self.ifname = ifs[:16].strip("\x00")
        return f

    def configure(self, subnet=None):
        if subnet is not None:
            if call("ip link set %s up" % self.name, shell=True) != 0:
                raise TunTapException("can`t set %s up" % self.name)
            if call("ip addr add %s dev %s" % (subnet, self.name), shell=True) != 0:
                raise TunTapException("can`t set subnet for interface %s" % self.name)

    
    def read(self):
        pass
    
    def write(self):
        pass

import os
import fcntl
import struct
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
    
    def read(self):
        self.fd.read()
    
    def write(self):
        pass
    

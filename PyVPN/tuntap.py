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
    def __init__(self, name="tun0"):
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
        self.sock.recv(4)
        packet = Packet.read_from_socket(self.sock, header_safe=True)
        print "read from tun %s" % packet
        return packet

    def write_packet(self, packet):
        self.sock.send(packet.data)
        print "write to tun %s" % packet
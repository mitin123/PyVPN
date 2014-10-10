import os
import select

from gevent import spawn

from tuntap import Tun
from utils import create_logger
from net import VPNServerConnection
from config import VPNClientConfig, InvalidConfigException

class VPNClient(object):
    def __init__(self):
        self.logger = create_logger(name="PyVPN Client Logger", file=os.path.join(".", "client.log"))

        try:
            self.config = VPNClientConfig(path_to_config="./client.conf")
        except InvalidConfigException as e:
            self.logger.error("loading config failed: %s" % e.msg)
            exit(-1)

        # tunneling connection to vpn server
        self.net = VPNServerConnection(host=self.config.server["host"], port=self.config.server["port"])

        self.tt = Tun(name="tun0")
        self.tt.configure(subnet=self.config.subnet)

    def _forward_data_from_net(self):
        print "start _forward_data_from_net"
        while True:
            self.tt.write_packet(self.net.read_packet())

    def _forward_data_from_tun(self):
        print "start _forward_data_from_tun"
        while True:
            self.net.write_packet(self.tt.read_packet())

    # simple bridge mode, just for testing purposes
    def start_bridge(self):

        g1 = spawn(self._forward_data_from_net)
        g2 = spawn(self._forward_data_from_tun)

        g1.join()
        g2.join()

        #self.net.sock.fileno(), self.tt.fd.fileno()

        """
        fds = [self.net.sock.fileno(), self.tt.fd.fileno()]
        epoll = select.epoll()
        epoll.register(self.net.sock.fileno(), select.EPOLLIN)
        epoll.register(self.tt.fd.fileno(), select.EPOLLIN)

        try:
            connections = {}; requests = {}; responses = {}
            while True:
                events = epoll.poll(1)
                for fileno, event in events:
                    if fileno == self.net.sock.fileno():
                        pass # read from network interface, write to tunneling device (forward)
                    if fileno == self.tt.fd.fileno():
                        pass # read from tunneling device, write to network interface
        finally:
            epoll.unregister(self.net.sock.fileno())
            epoll.unregister(self.tt.fd.fileno())
            epoll.close()
            self.net.close()
        """

if __name__ == "__main__":
    client = VPNClient()
    client.start_bridge()

import os
from socket import AF_INET, inet_pton
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

        self.net.sock.send(inet_pton(AF_INET, self.config.ip))

        self.tt = Tun(name="tun0")
        self.tt.configure(ip=self.config.ip, mask=self.config.mask)

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


if __name__ == "__main__":
    client = VPNClient()
    client.start_bridge()

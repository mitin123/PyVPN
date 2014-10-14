import os
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
        # TODO: make some factory for creating instance of encrypted connection,
        # after create, invoke method for auth handshake by some interface (f.e. .make_auth())
        # inject auth and encrypt objects
        self.net = VPNServerConnection(host=self.config.server["host"], port=self.config.server["port"], config=self.config)

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

    def start(self):
        g1 = spawn(self._forward_data_from_net)
        g2 = spawn(self._forward_data_from_tun)
        g1.join()
        g2.join()


if __name__ == "__main__":
    client = VPNClient()
    client.start()

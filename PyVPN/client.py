import os
from gevent import spawn

from tuntap import Tun
from utils import create_logger
from net import VPNServerConnection
from config import VPNClientConfig, InvalidConfigException
from crypto import CryptoPool
from auth import AuthPool

class VPNClient(object):
    def __init__(self, tun_name="tun0"):
        self.tun_name = tun_name

        self.logger = create_logger(name="PyVPN Client Logger", file=os.path.join(".", "client.log"))
        try:
            self.config = VPNClientConfig(path_to_config="./client.conf")
        except InvalidConfigException as e:
            self.logger.error("loading config failed: %s" % e.msg)
            exit(-1)

        self.crypto_pool = CryptoPool(self)
        self.auth_pool = AuthPool(self)

        self.crypto = self.crypto_pool.get(self.config.crypto_no)


    def _forward_data_from_net(self):
        self.logger.info("start forwarder from net")
        while True:
            self.tt.write_packet(self.net.read_packet())

    def _forward_data_from_tun(self):
        self.logger.info("start forwarder from tun")
        while True:
            self.net.write_packet(self.tt.read_packet())

    def start(self):
        try:
            # tunneling connection to vpn server
            # TODO: make some factory for creating instance of encrypted connection,
            # after create, invoke method for auth handshake by some interface (f.e. .make_auth())
            # inject auth and encrypt objects
            self.net = VPNServerConnection(host=self.config.server["host"], port=self.config.server["port"], app=self)
            self.tt = Tun(name=self.tun_name)
            self.tt.configure(ip=self.config.ip, mask=self.config.mask)
        except Exception as e:
            self.logger.error("start failed: %s" % e)
            exit(1)

        print "client ok"

        g1 = spawn(self._forward_data_from_net)
        g2 = spawn(self._forward_data_from_tun)
        g1.join()
        g2.join()


if __name__ == "__main__":
    client = VPNClient(tun_name="tun0")
    client.start()

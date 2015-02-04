import os
from gevent import spawn
from logging import INFO
from tuntap import Tun
from utils import create_logger
from net import VPNServerConnection
from config import VPNClientConfig

import traceback

client_logger = create_logger(name="PyVPN Client Logger", file=os.path.join(".", "client.log"), level=INFO)

class VPNClient(object):
    args_config = ["tun_name"]

    def __init__(self, **kwargs):
        self.logger = client_logger

        self.config = VPNClientConfig(path_to_config="./client.conf")

        overrides = ( (k,v) for k,v in kwargs.iteritems() if k in VPNClient.args_config )
        overrides = dict(overrides)

        self.config.update(overrides)

    def _forward_data_from_net(self):
        self.logger.info("start forwarder from net")
        while True:
            self.tt.write_packet(self.net.read_packet())

    def _forward_data_from_tun(self):
        self.logger.info("start forwarder from tun")
        while True:
            self.net.write_packet(self.tt.read_packet())

    def _connect_and_configure(self):
        self.net = VPNServerConnection(host=self.config.server["host"], port=self.config.server["port"], app=self)
        self.tt = Tun(name=self.config.tun_name)
        self.tt.configure(ip=self.config.ip, mask=self.config.mask)

    def start(self):
        self._connect_and_configure()
        self.logger.info("connect and configure ok")
        g1 = spawn(self._forward_data_from_net)
        g2 = spawn(self._forward_data_from_tun)
        self.logger.info("client ok")
        print "client ok"
        g1.join()
        g2.join()

if __name__ == "__main__":
    client = None
    try:
        client = VPNClient(config="./client.conf", tun_name="tun0")
        client.start()
    except Exception as e:
        client_logger.error("client failed: %s" % e)
        client_logger.error(traceback.format_exc())
        traceback.print_exc()
        exit(-1)
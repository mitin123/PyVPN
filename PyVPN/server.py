import select

from tuntap import Tun
from utils import create_logger
from net import VPNServerConnection
from config import VPNClientConfig, InvalidConfigException

class VPNServer(object):
    def __init__(self, tt=None):
        self.logger = create_logger(name="PyVPN Server Logger", file="./server.log")

        try:
            self.config = VPNClientConfig(path_to_config="./server.conf")
        except InvalidConfigException as e:
            self.logger.error("loading config failed: %s" % e.msg)
            exit(-1)


if __name__ == "__main__":
    pass
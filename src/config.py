import yaml
from utils import AttrDict
from vpnexcept import VPNException


class InvalidConfigException(VPNException):
    pass

class VPNConfig(AttrDict):
    def __init__(self, path_to_config=None):
        self.__path = path_to_config or self.__class__.__default_config_file
        self.read_config()
        self.check()
        #self.validate()

    def read_config(self):
        try:
            with open(self.__path) as config_file:
                self.update(yaml.load(config_file))
        except Exception:
            raise InvalidConfigException("configuration file reading failed")

    def validate(self):
        for validator in self.__class__.__conf_validators:
            if not validator(self.config):
                raise InvalidConfigException("validation failed")


class VPNClientConfig(VPNConfig):
    __default_config_file = "/etc/pyvpn/client.conf"
    __conf_validators = [
        lambda c: "subnet" in c,
        lambda c: "netmask" in c,
    ]
    def check(self):
        if "ip" not in self:
            self["ip"] = "0.0.0.0" # for dynamically allocation


class VPNServerConfig(VPNConfig):
    __default_config_file = "/etc/pyvpn/server.conf"
    __conf_validators = [
        lambda c: "server" in c,
    ]
    def check(self):
        pass

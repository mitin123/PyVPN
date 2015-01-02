import yaml

from vpnexcept import VPNException


class InvalidConfigException(VPNException):
    pass

class VPNConfig(object):
    def __init__(self, path_to_config=None):
        self.__path = path_to_config or self.__class__.__default_config_file
        self.read_config()
        #self.validate()

    def read_config(self):
        try:
            with open(self.__path) as config_file:
                self.config = yaml.load(config_file)
        except Exception:
            raise InvalidConfigException("configuration file reading failed")

    def validate(self):
        for validator in self.__class__.__conf_validators:
            if not validator(self.config):
                raise InvalidConfigException("validation failed")

    def __getattr__(self, attr):
        if attr in self.config:
            return self.config[attr]
        else:
            return super(VPNConfig, self).__getattr__(attr)

    def __getitem__(self, item):
        if item in self.config:
            return self.config[item]

    def __setitem__(self, key, value):
        self.config[key] = value

    def __iter__(self):
        return iter(self.config)

class VPNClientConfig(VPNConfig):
    __default_config_file = "/etc/pyvpn/client.conf"
    __conf_validators = [
        lambda c: "subnet" in c,
        lambda c: "netmask" in c,
    ]


class VPNServerConfig(VPNConfig):
    __default_config_file = "/etc/pyvpn/server.conf"
    __conf_validators = [
        lambda c: "subnet" in c,
        lambda c: "netmask" in c,
    ]

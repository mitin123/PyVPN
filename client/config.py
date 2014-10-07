import yaml
from vpnexcept import VPNException

class InvalidConfigException(VPNException):
    pass

class VPNClientConfig(object):
    __conf_validators = [
        lambda c: subnet in c,
        lambda c: netmask in c,
    ]
    
    def __init__(self, path_to_config=None):
        self.__path = path_to_config or "/etc/pyvpn/pyvpn.conf"
        self.read_config()
        #self.validate()
        
    def read_config(self):
        try:
            with open(self.__path) as config_file:
                self.config = yaml.load(config_file)
        except Exception:
            ex = InvalidConfigException()
            ex.msg = "configuration file reading failed"
            raise ex
    
    def validate():
        for validator in __conf_validators:
            if not validator(self.config):
                ex = InvalidConfigException()
                ex.msg = "wtf"
                raise ex
    
    def __getattr__(self, attr):
        if attr in self.config:
            return self.config[attr]
        else:
            return super(A, self).__getattr__(attr)

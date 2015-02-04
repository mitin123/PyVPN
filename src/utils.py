import logging
from collections import defaultdict

def create_logger(name="default", file="./app.log", level=logging.WARNING):
    logger = logging.getLogger(name)
    hdlr = logging.FileHandler(file)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr) 
    logger.setLevel(level)
    return logger

class AttrDict(dict):
    def __init__(self, d=None):
        if isinstance(d, dict):
            self.update(d)
        elif d is None:
            pass
        else:
            raise ValueError("argument must be a dict or extends dict, not %s" % type(d))

    def update(self, d):
        for k,v in d.iteritems():
            if isinstance(v, dict):
                self[k] = AttrDict(v)
            else:
                self[k] = v

    def __getattribute__(self, attr):
        if attr in self:
            return self[attr]
        else:
            return super(AttrDict, self).__getattribute__(attr)

    __setattr__ = dict.__setitem__

class AbstractPool(object):
    def __init__(self):
        self.__classes = {}
        self.__pool = defaultdict(list)

    def register(self, cls):
        if hasattr(cls, "_index"):
            self.__classes[cls._index] = cls

    def alloc(self, index):
        if index in self.__classes:
            new = self.__classes[index]()
            self.__pool[index].append(new)
            return new
        else:
            self.not_found(index)

    def not_found(self, index):
        raise Exception("class with index %d not found" % index)

def address_in_subnet(subnet, address):
    pass
from gevent.os import tp_read, tp_write

class NonblockFileWrapper(object):
    def __init__(self, fd):
        self.fd = fd

    def read(self, nbytes):
        return tp_read(self.fd, nbytes)

    def write(self, buffer):
        tp_write(self.fd, buffer)

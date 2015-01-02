class VPNException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __repr__(self):
        return "<VPNException: '%s'>" % self.msg

    __str__ = __repr__
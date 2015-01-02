class FileToSocketAdapter(object):
    def __init__(self, file):
        self.file = file

    def recv(self, nbytes):
        return self.file.read(nbytes)

    def send(self, buff):
        self.file.write(buff)

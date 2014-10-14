from gevent import spawn, socket

from utils import create_logger
from config import VPNServerConfig, InvalidConfigException
from net import VPNClientConnection

class VPNServer(object):
    def __init__(self):
        self.logger = create_logger(name="PyVPN Server Logger", file="./server.log")

        try:
            self.config = VPNServerConfig(path_to_config="./server.conf")
        except InvalidConfigException as e:
            self.logger.error("loading config failed: %s" % e.msg)
            exit(-1)

        self.connections = {}
        self.address_pool = {}

    def handle(self, conn, addr):
        try:
            client_connection = VPNClientConnection(conn)
        except: # handle case if auth error or something failed
            pass

        self.connections[client_connection.ip] = client_connection

        print "Client connected by", addr, client_connection.ip

        while True:
            packet = client_connection.read_packet()
            dst_ip = packet.header["dst"]
            if dst_ip in self.connections:
                self.connections[dst_ip].write_packet(packet)
                print "packet was sent"
            else:
                print "!!! client for this packet not found"

    def serve_forever(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind((self.config.server["host"], self.config.server["port"]))
        except:
            print "socket error"
            exit(1)
        s.listen(1024)

        print "start server"

        while True:
            conn, addr = s.accept()
            spawn(self.handle, conn, addr)

if __name__ == "__main__":
    server = VPNServer()
    server.serve_forever()
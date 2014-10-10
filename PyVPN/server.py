import select
import struct
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

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind((self.config.server["host"], self.config.server["port"]))
        except:
            print "socket error"
            exit(1)
        s.listen(1024)

        while True:
            conn, addr = s.accept()

            client_connection = VPNClientConnection(conn)

            ip = struct.unpack("i", conn.recv(4))[0]

            print "Client connected by", addr, ip

            self.connections[ip] = client_connection

            spawn(self.handle, client_connection)

    def handle(self, client_connection):
        while True:
            print client_connection.sock
            packet = client_connection.read_packet()
            print "src = ", packet.src_asstring()
            print "dst = ", packet.dst_asstring()
            if packet.dst in self.connections:
                self.connections[packet.dst].write_packet(packet)
                print "packet was sent"
            else:
                print "!!! client for this packet not found"

            #client_connection.write_packet(Packet("Good By!"))


    def serve_forever(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if __name__ == "__main__":
    server = VPNServer()
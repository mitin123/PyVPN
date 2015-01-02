from gevent import spawn, socket

from utils import create_logger
from config import VPNServerConfig, InvalidConfigException
from net import VPNClientConnection
from vpnexcept import VPNException

from crypto import CryptoPool
from auth import AuthPool

import traceback

server_logger = create_logger(name="PyVPN Server Logger", file="./server.log")

class VPNServer(object):
    def __init__(self):
        self.logger = server_logger

        self.config = VPNServerConfig(path_to_config="./server.conf")

        self.crypto_pool = CryptoPool(self)
        self.auth_pool = AuthPool(self)
        self.auth = self.auth_pool.get(self.config.auth_no)

        self.connections = {}
        self.address_pool = {}

    def handle_connection(self, conn, addr):
        client_connection = None
        try:
            client_connection = VPNClientConnection(conn, self)
            self.connections[client_connection.ip] = client_connection
        except Exception as e: # handle case if auth error or something failed
            self.logger.error(e)
            self.logger.error(traceback.format_exc())
            traceback.print_exc()
            conn.close()
            return

        print addr
        print client_connection.__dict__
        self.logger.info("Client connected by %s:%s" % addr)

        while True:
            packet = client_connection.read_packet()
            dst_ip = packet.header["dst"]
            print "dst_ip =", dst_ip
            if dst_ip in self.connections:
                self.connections[dst_ip].write_packet(packet)
                print "packet was sent"
            else:
                print "client for packet not found"

    def serve_forever(self, listen_socket):
        while True:
            conn, addr = listen_socket.accept()
            spawn(self.handle_connection, conn, addr)

    def start(self):
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listen_socket.bind((self.config.server["host"], self.config.server["port"]))

        listen_socket.listen(1024)

        self.logger.info("starting server...")
        print "start server"

        p = spawn(self.serve_forever, listen_socket)
        p.join()

if __name__ == "__main__":
    server = None
    try:
        server = VPNServer()
    except Exception as e:
        server_logger.error("init server failed: %s" % e.msg)
        traceback.print_exc()
        exit(-1)

    server.start()
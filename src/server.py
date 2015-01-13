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
            if client_connection.session_has_expired():
                client_connection.update_session_key()

            packet = client_connection.read_packet()
            dst_ip = packet.header["dst"]
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
        listen_socket.bind(("0.0.0.0", self.config.port))

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
        traceback.print_exc()
        server_logger.error("init server failed: %s" % e.msg)
        exit(-1)

    server.start()
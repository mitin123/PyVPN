from gevent import spawn, socket
from logging import INFO
from utils import create_logger
from config import VPNServerConfig
from net import VPNClientConnection

import traceback

server_logger = create_logger(name="PyVPN Server Logger", file="./server.log", level=INFO)

class VPNServer(object):
    args_config = []

    def __init__(self, **kwargs):
        self.logger = server_logger
        self.connections = {}
        self.address_pool = {}

        self.config = VPNServerConfig(path_to_config="./server.conf")

        overrides = ( (k,v) for k,v in kwargs.iteritems() if k in VPNServer.args_config )
        overrides = dict(overrides)
        self.config.update(overrides)

    def handle_connection(self, conn, addr):
        client_connection = None
        try:
            client_connection = VPNClientConnection(conn, self)
        except Exception as e: # handle case if auth error or something failed
            self.logger.error(e)
            self.logger.error(traceback.format_exc())
            traceback.print_exc()
            conn.close()
            return

        self.logger.info("Client connected by %s:%s" % addr)
        self.connections[client_connection.ip] = client_connection

        while True: # forwarding loop
            if client_connection.session_has_expired():
                client_connection.update_session_key()

            packet = client_connection.read_packet()
            dst_ip = packet.header["dst"]
            if dst_ip in self.connections:
                self.connections[dst_ip].write_packet(packet)

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
        server_logger.error("init server failed: %s" % e)
        exit(-1)

    server.start()
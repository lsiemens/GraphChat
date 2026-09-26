"""
Simple HTTP server using sockets and poll.
"""

import logging
import select
import socket

from . import http_connection


logger = logging.getLogger(__name__)


class HTTPServer:
    _backlog = 16
    _max_connections = 1024

    def __init__(self, host, port, process_request):
        self._host = host
        self._port = port
        self._process_request = process_request

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            try:
                server.bind((self._host, self._port))
                server.listen(self._backlog)
                server.setblocking(False)
            except OSError:
                logger.exception("Failure while binding socket.")
                raise

            poller = select.poll()
            poller.register(server.fileno(), select.POLLIN)
            connections = {}

            print(f"HTTP server listening on port {self._port} ...")
            try:
                while True:
                    events = poller.poll()

                    for fd, event in events:
                        if fd == server.fileno():
                            try:
                                client = server.accept()
                                client[0].setblocking(False)
                            except OSError:
                                logger.warning("Failed to accept connection.")
                                continue

                            conn = http_connection.HTTPConnection(*client, self._process_request)
                            connections[conn.fileno()] = conn
                            poller.register(conn.fileno(), select.POLLIN)
                            conn.POLLOUT_state = False
                            print(f"New connection from {client[1]}")
                            continue

                        conn = connections[fd]
                        if event & select.POLLIN:
                            conn.on_POLLIN()

                        if event & select.POLLOUT:
                            conn.on_POLLOUT()

                        if conn.need_POLLOUT() != conn.POLLOUT_state:
                            flags = select.POLLIN | (select.POLLOUT if conn.need_POLLOUT() else 0)
                            poller.modify(conn.fileno(), flags)
                            conn.POLLOUT_state = conn.need_POLLOUT()

                        if conn.is_closed:
                            poller.unregister(fd)
                            del connections[fd]

            except KeyboardInterrupt:
                print("\nClosing HTTP server!")

if __name__ == "__main__":
    logging.basicConfig(filename="http_server.log", level=logging.INFO)
    print("Reply to all requests with 200 and Connection:close")
    server = HTTPServer("0.0.0.0", 8000, http_connection.process_request_all_good)
    server.start()

"""
Simple HTTP server using sockets.
"""

import select
import socket

import http_message

class HTTPServer:
    _backlog = 16
    _timeout = 10
    _max_connections = 1024
    _block_size = 1

    def __init__(self, host="0.0.0.0", port=8000):
        self._host = host
        self._port = port

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            try:
                server.bind((self._host, self._port))
                server.listen(self._backlog)
                server.setblocking(False)
            except OSError as e:
                print(f"Error when binding socket: {e}")
                raise

            sockets_read, sockets_write = [], []
            buffer_HTTP_requests = []
            buffers_write = []
            close_on_write = []

            print(f"HTTP server listening on port {self._port} ...")
            try:
                while True:
                    readable, writable, errors = select.select([server] + sockets_read, sockets_write, [], self._timeout)

                    for soc in readable:
                        if soc is server:
                            try:
                                connection, address = server.accept()
                                connection.setblocking(False)
                            except OSError as e:
                                print(f"Warning failed to accept connection: {e}")
                                continue
                            sockets_read.append(connection)
                            buffer_HTTP_requests.append(http_message.HTTPRequest())
                            print(f"New connection from {address}")
                        else:
                            index = sockets_read.index(soc)
                            data = soc.recv(self._block_size)
                            if data:
                                HTTP_request = buffer_HTTP_requests[index]
                                HTTP_request._buffer += data

                                try:
                                    HTTP_request.update()
                                except http_message.HTTPError as e:
                                    print(f"Warning failed to update HTTP request: {e}")

                                    sockets_read.pop(index)
                                    buffer_HTTP_requests.pop(index)

                                    if (soc in sockets_write):
                                        write_index = sockets_write.index(soc)
                                        sockets_write.pop(write_index)
                                        buffers_write.pop(write_index)

                                    if (soc in writable):
                                        writable.remove(soc)

                                    if (soc in close_on_write):
                                        close_on_write.remove(soc)

                                    soc.sendall(http_message.CriticalHTTPError(400, close=True))
                                    soc.close()
                                    continue

                                if HTTP_request.is_ready:
                                    # Create new HTTP_request for buffer
                                    tmp_buffer = HTTP_request._buffer
                                    buffer_HTTP_requests[index] = http_message.HTTPRequest(tmp_buffer)

                                    HTTP_reply = self.process_requests(HTTP_request)

                                    try:
                                        HTTP_reply = HTTP_reply.format()
                                    except http_message.HTTPError as e:
                                        print(f"Warning failed to format HTTP reply: {e}")
                                        HTTP_reply = http_message.CriticalHTTPError(500, close=False)

                                    if soc not in sockets_write:
                                        sockets_write.append(soc)
                                        buffers_write.append(HTTP_reply)
                                    else:
                                        write_index = sockets_write.index(soc)
                                        buffers_write[write_index] += HTTP_reply

                                    if "connection" in HTTP_request.headers:
                                        if HTTP_request.headers["connection"] == "close":
                                            if soc not in close_on_write:
                                                close_on_write.append(soc)
                            else:
                                print("Connection closed by client")
                                sockets_read.pop(index)
                                buffer_HTTP_requests.pop(index)

                                if soc in sockets_write:
                                    write_index = sockets_write.index(soc)
                                    sockets_write.pop(write_index)
                                    buffers_write.pop(write_index)

                                if soc in close_on_write:
                                    close_on_write.remove(soc)

                                if soc in writable:
                                    writable.remove(soc)

                                soc.close()

                    print(f"\n\nWB: {buffers_write}")
                    for soc in writable:
                        index = sockets_write.index(soc)
                        try:
                            print(f"\n\n WB pre: {buffers_write[index]}")
                            bytes_sent = soc.send(buffers_write[index][:self._block_size])
                            buffers_write[index] = buffers_write[index][bytes_sent:]
                            print(f"\n\n WB post: {buffers_write[index]}")
                            if bytes_sent == 0:
                                sockets_write.pop(index)
                                buffers_write.pop(index)

                                if soc in close_on_write:
                                    print("Connection closed by request")
                                    close_on_write.remove(soc)

                                    read_index = sockets_read.index(soc)
                                    sockets_read.pop(read_index)
                                    buffer_HTTP_requests.pop(read_index)

                                    soc.close()
                        except BlockingIOError:
                            print("Client buffer is full, continue")
                        except (ConnectionResetError, BrokenPipeError, OSError) as e:
                            print("Connection closed during write")
                            sockets_write.pop(index)
                            buffers_write.pop(index)

                            if soc in close_on_write:
                                close_on_write.remove(soc)

                            if soc in sockets_read:
                                read_index = sockets_read.index(soc)
                                sockets_read.pop(read_index)
                                buffer_HTTP_requests.pop(read_index)

                            soc.close()

            except KeyboardInterrupt:
                print("\nClosing HTTP server!")

    def process_requests(self, HTTP_request):
        HTTP_reply = http_message.HTTPReply()
        # TODO process through pipeline
        # pipeline(HTTP_request, HTTP_reply)

        # TODO process through state machine
        # state_machine(HTTP_request, HTTP_reply)

        HTTP_reply.status_code = 200 # TEMP until processing is in place
        HTTP_reply.headers["connection"]="keep-alive"
        return HTTP_reply

if __name__ == "__main__":
    server = HTTPServer()
    server.start()

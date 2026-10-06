"""
Manage a single HTTP connection
"""

import logging

from . import exceptions
from . import http_message


logger = logging.getLogger(__name__)


class HTTPConnection:
    _timeout = 1000
    _block_size = 1024

    def __init__(self, socket, address, process_request_core):
        self._socket = socket
        self._address = address
        self._fileno = self._socket.fileno()
        self._is_closed = False
        self.POLLOUT_state = None # for external use only

        self._process_request_core = process_request_core

        # one request can contain the data from multiple HTTP requests in the
        # internal buffer while its being parsed. So this acts like a HTTP
        # request buffer.
        self._HTTP_request = http_message.HTTPRequest()
        # each reply can only contain data from a single reply so process
        # replies in a reply que
        self._HTTP_reply_que = []

    @property
    def is_closed(self):
        return self._is_closed

    def need_POLLOUT(self):
        return len(self._HTTP_reply_que) != 0

    def fileno(self):
        return self._fileno

    def on_POLLIN(self):
        if self._is_closed:
            return

        try:
            data = self._socket.recv(self._block_size)
            self._HTTP_request.buffer += data
        except OSError:
            logger.warning("Could not read from socket, closing connection.")
            self._is_closed = True
            self._socket.close()
            return

        if len(data) == 0:
            logger.info("Connection closed by the client.")
            self._is_closed = True
            self._socket.close()
            return

        try:
            self._HTTP_request.update()
        except exceptions.HTTPError as e:
            status, message = self.exception_handler(e)
            HTTP_error = http_message.MinorHTTPError(status, "close")
            HTTP_error.body = message
            HTTP_error.headers["content-type"] = "txt/plain"
            self._HTTP_reply_que.append(HTTP_error)
            return
            # TODO disable reading

        if self._HTTP_request.is_ready:
            buffer = self._HTTP_request.buffer
            self._process_request(self._HTTP_request)
            self._HTTP_request = http_message.HTTPRequest(buffer)

    def on_POLLOUT(self):
        if self._is_closed:
            return

        if len(self._HTTP_reply_que) == 0:
            return
        current_reply = self._HTTP_reply_que[0]

        if not current_reply.serialized:
            try:
                current_reply.serialize()
            except exceptions.HTTPError as e:
                status, message = self.exception_handler(e)
                HTTP_error = http_message.MinorHTTPError(status, "close")
                HTTP_error.body = message
                HTTP_error.headers["content-type"] = "txt/plain"
                self._HTTP_reply_que[0] = HTTP_error
                current_reply = self._HTTP_reply_que[0]
                # catch exception from serialize in Minor error

        if len(current_reply.buffer) == 0:
            if "connection" in current_reply.headers:
                if "close" in current_reply.headers["connection"].lower():
                    self._is_closed = True
                    self._socket.close()

            try:
                del self._HTTP_reply_que[0]
            except KeyError:
                logger.exception("Could not delete a completed HTTP reply")
                # TODO more checking and recovery

            return

        try:
            data_sent = self._socket.send(current_reply.buffer[:self._block_size])
            current_reply.buffer = current_reply.buffer[data_sent:]
        except (OSError, BrokenPipeError, ConnectionResetError):
            logger.warning("Connection closed during write.")
            self._is_closed = True
            self._socket.close()
        except BlockingIOError:
            pass  # try again

    def _process_request(self, HTTP_request):
        # The response to a HEAD request must be identical to that of a GET
        # request with all other properties the same, but with no body/content
        # in the HTTP reply.
        method, target, HTTP_version = HTTP_request.request_line
        is_head = (method == "HEAD")
        if is_head:
            HTTP_request.request_line = ("GET", target, HTTP_version)
        HTTP_reply = http_message.HTTPReply(as_head=is_head)

        # potential extra processing

        if HTTP_reply.status_code is None:
            try:
                self._process_request_core(HTTP_request, HTTP_reply)
            except exceptions.HTTPError as e:
                status, message = self.exception_handler(e)
                HTTP_error = http_message.MinorHTTPError(status, "close")
                HTTP_error.body = message
                HTTP_error.headers["content-type"] = "txt/plain"
                self._HTTP_reply_que.append(HTTP_error)
        self._HTTP_reply_que.append(HTTP_reply)


    def exception_handler(self, exception):
        message = f"HTTP request failed with `{exception}`"
        if isinstance(exception, exceptions.NotFoundError):
            status = 404
            logger.info("HTTP request failed: resource not found")
        elif isinstance(exception, exceptions.ParseError):
            status = 400
            logger.info("HTTP request failed: parse failure")
        elif isinstance(exception, exceptions.ProtocolError):
            status = 400
            logger.info("HTTP request failed: protocol violation")
        elif isinstance(exception, exceptions.SerializeError):
            status = 500
            logger.exception("HTTP request failed: serialization failure")
        else:
            status = 500
            logger.exception("HTTP request failed")

        return status, message



def process_request_all_good(HTTP_request, HTTP_reply):
    HTTP_reply.status_code = 200
    HTTP_reply.headers["connection"] = "close"

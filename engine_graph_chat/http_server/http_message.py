"""
HTTP messages.
"""

import re
import socket
import email.utils

STATUS_CODES = {200:"OK", 201:"Created",
                400:"Bad Request", 404:"Not Found",
                411:"Length Required", 413:"Content Too Large",
                500:"Internal Server Error", 501:"Not Implemented",
                505:"HTTP Version Not Supported"}
PROTOCOL = "HTTP/1.1"
ENCODING_HEADER = "iso-8859-1"
ENCODING_BODY = "utf-8"
# character sets listed by CloudFlare
# https://developers.cloudflare.com/rules/transform/request-header-modification/reference/header-format/
VALID_HEADER_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_\-]{0,255}$")
VALID_HEADER_VALUE = re.compile(r"^(?!:)[ -~]{0,4095}$")

def is_HTTP_header_field(name, value):
    if not re.match(VALID_HEADER_NAME, name):
        return False
    if not re.match(VALID_HEADER_VALUE, value):
        return False
    return True

def CriticalHTTPError(status_code, close):
    """To be used when HTTP_reply fails"""
    connection_value = "close" if close else "keep-alive"
    reply = f"HTTP/1.1 {status_code} {STATUS_CODES[status_code]}\r\n" \
            f"connection: {connection_value}\r\n\r\n"
    return reply.encode(ENCODING_HEADER)

class HTTPError(Exception):
    """Errors when parsing HTTP messages"""
    pass

class HTTPReply:
    def __init__(self):
        self.status_code = None
        self.headers = {"date":email.utils.formatdate(usegmt=True)}
        self.body = ""

    def format(self):
        # Format headers
        headers = {}
        for name, value in self.headers.items():
            if is_HTTP_header_field(name, value):
                headers[name.lower()] = value
            else:
                raise HTTPError(f"Error: malformed header field {repr(key)}:{repr(value)}")

        # Validate status code
        status_code = self.status_code
        if self.status_code not in STATUS_CODES:
            raise HTTPError(f"Error: the status code {self.status_code} is not implemented!")
        reason_phrase = STATUS_CODES[self.status_code]

        # Format body
        body = self.body.encode(ENCODING_BODY)
        if self._force_no_content(status_code):
            body = b""
        if len(body) != 0:
            headers["content-length"] = str(len(body))
            if "content-type" not in headers:
                raise HTTPError("Error: replies with a body must declare the content type!")

        # Format reply
        reply = f"{PROTOCOL} {status_code} {reason_phrase}\r\n"
        for name, value in headers.items():
            reply += f"{name}: {value}\r\n"
        reply = reply.encode(ENCODING_HEADER) + b"\r\n" + body
        print(f"\n\nFormat: {reply}")
        return reply

    def _force_no_content(self, status_code):
        """Replies that must not have content"""
        return (status_code < 200) or (status_code in [204, 205, 304])

class HTTPRequest:
    _max_body_size = 2**20
    _max_header_size = 8190

    def __init__(self, buffer=b""):
        self.first_line = None # None or (Method, target, protocol)
        self.headers = {}
        self.body = b""

        self._buffer = buffer
        self._bytes_header = 0
        self._is_ready = False
        self._reading_head = True

    @property
    def is_ready(self):
        return self._is_ready

    def _get_line(self):
        """Reading line by line for the header"""
        if b"\n" in self._buffer:
            line, self._buffer = self._buffer.split(b"\n", 1)
            self._bytes_header += len(line) + 1
            if len(line) > 0:
                if line.endswith(b"\r"):
                    line = line[:-1]
            return line.decode(ENCODING_HEADER)
        else:
            return None

    def update(self):
        if self._is_ready:
            return

        if self._reading_head:
            while (line := self._get_line()) is not None:
                # Check for end of the header
                if len(line) == 0:
                    if "content-length" in self.headers:
                        length = self.headers["content-length"]
                        if not length.isdigit():
                            print("Warning header-field \"content-length\" is malformed")
                            raise HTTPError("Invalid characters in \"content-length\"")
                        self.headers["content-length"] = int(self.headers["content-length"])
                    self._reading_head = False
                    break

                # process the first line
                if self.first_line is None:
                    parts = line.split()
                    if len(parts) != 3:
                        print("Warning malformed first line")
                        raise HTTPError("Could not read METHOD, TARGET, PROTOCOL")
                    self.first_line = (parts[0].upper(), parts[1], parts[2].upper())
                    continue

                if ":" not in line:
                    print("Warning malformed header-field")
                    raise HTTPError("Header-field missing \":\"")

                name, value = line.split(":", 1)

                if not is_HTTP_header_field(name, value):
                    print("Warning malformed header-field")
                    raise HTTPError("Invalid characters in header-field name or value")

                value = value.lstrip()
                self.headers[name.lower()] = value

            if self._reading_head:
                if (self._bytes_header + len(self._buffer) > self._max_header_size):
                    print("Warning header is larger than the maximum value")
                    raise HTTPError("Header exceeds the maximum size")
            else:
                if (self._bytes_header > self._max_header_size):
                    print("Warning header is larger than the maximum value")
                    raise HTTPError("Header exceeds the maximum size")


        if (not self._reading_head) and ("content-length" not in self.headers):
            self._is_ready = True
            return

        if (not self._reading_head) and ("content-length" in self.headers):
            length = self.headers["content-length"]

            bytes_left = max(length - len(self.body), 0)
            bytes_take = min(len(self._buffer), bytes_left)

            self.body   += self._buffer[:bytes_take]
            self._buffer = self._buffer[bytes_take:]

            if len(self.body) > self._max_body_size:
                print("Warning body is larger than the maximum value")
                raise HTTPError("Body exceeds the maximum size")

            if len(self.body) > length:
                print("Warning body is malformed")
                raise HTTPError("Body exceeds the length given by \"content-length\"")

            if len(self.body) == length:
                self._is_ready = True
                return

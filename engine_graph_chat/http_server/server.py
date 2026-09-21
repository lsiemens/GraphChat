"""
Simple HTTP server using sockets.
"""

import socket

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
VALID_HEADER_NAME = "-_"
VALID_HEADER_VALUE = "_ :;.,\\/\"'?!(){}[]@<>=+-*#$&`|~^%"

def is_HTTP_header_name(name):
  chars = set(name)
  for char in chars:
    if (not char.isalnum()) and (char not in VALID_HEADER_NAME):
      return False
  return True

def is_HTTP_header_value(name):
  chars = set(name)
  for char in chars:
    if (not char.isalnum()) and (char not in VALID_HEADER_VALUE):
      return False
  return True

def HTTP_reply(status_code, reply_headers=None, body=""):
  if reply_headers is None:
    reply_headers = {}

  tmp_reply_headers = {}
  for key, value in reply_headers.items():
    if is_HTTP_header_name(key) and is_HTTP_header_value(value):
      tmp_reply_headers[key.lower()] = value
    else:
      raise ValueError(f"Error: malformed header field {key}:{value}")
  reply_headers = tmp_reply_headers

  if status_code not in STATUS_CODES:
    raise NotImplementedError(f"Error: the status code {status_code} is not implemented!")
  reason_phrase = STATUS_CODES[status_code]

  body = body.encode(ENCODING_BODY)
  reply_headers["content-length"] = str(len(body))
  if body != b"":
    if "content-type" not in reply_headers:
      raise ValueError("Error: replies with a body must declare the content type!")

  header = f"{PROTOCOL} {status_code} {reason_phrase}\r\n"
  for key, value in reply_headers.items():
    header += f"{key}: {value}\r\n"
  reply = header.encode(ENCODING_HEADER) + b"\r\n" + body
  return reply

class Server:
  _backlog = 16
  _retry_range = (0.01, 0.3)
  _max_header_lines = 256
  _max_content_length = 2**20

  def __init__(self, handle_HTTP_requests, host="0.0.0.0", port=8000):
    self._host = host
    self._port = port
    self._handle_HTTP_requests = handle_HTTP_requests

  def start(self):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
      soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

      try:
        soc.bind((self._host, self._port))
      except OSError as e:
        print(f"Error while binding socket: {e}")
        raise

      try:
        soc.listen(self._backlog)
      except OSError as e:
        print(f"Error when marking socket as passive: {e}")
        raise

      print(f"HTTP server listening on port {self._port} ...")
      try:
        while True:
          try:
            connection, address = soc.accept()
          except OSError as e:
            print(f"Warning failed to accept connection: {e}")
            continue

          with connection:
            self._process_connection(connection, address)
      except KeyboardInterrupt:
        print("\nClosing HTTP server!")

  def _process_connection(self, connection, address):
    with connection.makefile("rb") as soc_file:
      start_line = soc_file.readline().strip().decode(ENCODING_HEADER)
      header = {}
      body = b""
      is_EOH = False
      for i in range(self._max_header_lines):
        line = soc_file.readline().strip().decode(ENCODING_HEADER)
        if line != "":
          try:
            key, value = line.split(":", 1)
          except ValueError as e:
            print(f"Warning malformed header line: {e}")
            connection.sendall(HTTP_reply(400))
            return

          if is_HTTP_header_name(key) and is_HTTP_header_value(value):
            header[key.lower().strip()] = value.strip()
          else:
            print("Warning invalid characters in header line")
            connection.sendall(HTTP_reply(400))
            return
        else:
          is_EOH = True
          break

      if (not is_EOH):
        print("Warning header exceded the maximum length")
        connection.sendall(HTTP_reply(413))
        return

      try:
        method, target, protocol = start_line.split()
        method = method.upper().strip()
        target = target.strip()
        protocol = protocol.upper().strip()
      except ValueError as e:
        print(f"Warning malformed header start-line: {e}")
        connection.sendall(HTTP_reply(400))
        return

      if protocol != PROTOCOL:
        print("Warning unsupported HTTP protocol")
        connection.sendall(HTTP_reply(505))
        return

      if method in ["POST", "PUT", "PATCH"]:
        if "content-length" not in header:
          print("Warning requests with a body must include \"content-length\"")
          connection.sendall(HTTP_reply(411))
          return

      if "content-length" in header:
        if not header["content-length"].isdigit():
          print("Warning could not parse content-length")
          connection.sendall(HTTP_reply(400))
          return

        content_length = int(header["content-length"])
        if content_length > self._max_content_length:
          print("Warning header content-length is too large")
          connection.sendall(HTTP_reply(413))
          return
        body = soc_file.read(content_length).strip()

        if (len(body) != content_length):
          print("Warning the HTTP body does not match \"content-length\"")
          connection.sendall(HTTP_reply(400))
          return

      try:
        bytes_HTTP_reply = self._process_HTTP_requests((method, target, protocol), header, body)
      except Exception as e:
        print(f"Error while processing request from {address}: {e}")
        connection.sendall(HTTP_reply(500))
        return

      connection.sendall(bytes_HTTP_reply)

  def _process_HTTP_requests(self, first_line, header, body):
    return self._handle_HTTP_requests(first_line, header, body)

if __name__ == "__main__":
  def example_surver(first_line, header, body):
    method, target, protocol = first_line

    page = """<!DOCTYPE html>
    <html>
      <head>
        <title>Hello World!</title>
      </head>
      <body>
        <h1>Hello World</h1>
        <p>This page is being served from a basic HTTP server built from python</p>
      </body>
    </html>
    """
    reply = HTTP_reply(200, {"content-type":"text/html; charset=UTF-8"}, page)

    match method:
      case "HEAD":
        reply = reply.split(b"\r\n\r\n", 1)[0] + b"\r\n\r\n"
        return reply
      case "GET":
        return reply
      case _:
        return HTTP_reply(501)

  server = Server(example_surver)
  server.start()

"""
Simple HTTP server using sockets.

following "https://www.codementor.io/@joaojonesventura/building-a-basic-http-server-from-scratch-in-python-1cedkg0842"
"""

import urllib.parse
import os.path
import socket

root = os.path.realpath("./html")
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(1)
print(f"Socket server listening on port {SERVER_PORT} ...")

while True:
  client_connection, client_address = server_socket.accept()
  request = client_connection.recv(1024).decode()

  headers = request.split("\n")
  filename = headers[0].split()[1]
  filename = urllib.parse.unquote(filename)

  if filename == "/":
    filename = "/index.html"
  path = os.path.realpath(os.path.join(root, filename.lstrip("/")))

  is_valid_path = True
  if (not os.path.exists(path)):
    print(f"ERROR: path \"{path}\" does not exist!")
    is_valid_path = False

  if (not os.path.isfile(path)):
    print(f"ERROR: path \"{path}\" is not a file!")
    is_valid_path = False

  if os.path.commonpath([root, path]) != root:
    print(f"ERROR: path \"{path}\" is out side of \"./html\"!")
    is_valid_path = False

  response = "HTTP/1.0 404 NOT FOUND\r\n\r\n" \
             "File Not Found"

  if (is_valid_path):
    try:
      body = ""
      with open(path, "r") as fin:
        body = fin.read()

      response = "HTTP/1.0 200 OK\r\n" \
                 "Content-Type: text/html\r\n" \
                f"Content-Length: {len(body.encode('utf-8'))}\r\n" \
                 "Connection: close\r\n\r\n" \
                f"{body}"
    except:
      print(f"Error: failed to read file!")

      response = "HTTP/1.0 404 NOT FOUND\r\n\r\n" \
                 "File Not Found"

  client_connection.sendall(response.encode('utf-8'))
  client_connection.close()

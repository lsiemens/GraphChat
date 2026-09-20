"""
Simple HTTP server using sockets.

following "https://www.codementor.io/@joaojonesventura/building-a-basic-http-server-from-scratch-in-python-1cedkg0842"
"""

import socket

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
  print(request)

  body = ""
  with open("./html/index.html", "r") as fin:
    body = fin.read()

  response = "HTTP/1.0 200 OK\r\n" \
             "Content-Type: text/html\r\n" \
            f"Content-Length: {len(body.encode('utf-8'))}\r\n" \
             "Connection: close\r\n\r\n" \
            f"{body}"

  client_connection.sendall(response.encode('utf-8'))
  client_connection.close()

import socket

ADDR = ("127.0.0.1", 8080)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen()
conn, addr = server.accept()
print(f"Successfully connected with {conn}")
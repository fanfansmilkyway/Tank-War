import socket

ADDR = ("127.0.0.1", 8080) # Server IP
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
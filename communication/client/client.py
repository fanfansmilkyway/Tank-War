import socket

FORMAT = 'utf-8'
ADDR = ("127.0.0.1", 8080) # Server IP

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
print("[CONNECTION] Successfully connected with the server")

msg = client.recv(2024).decode(FORMAT)
print(msg)
client.send(b"Here is the client")
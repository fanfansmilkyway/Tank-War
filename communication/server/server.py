import socket
import threading

FORMAT = 'utf-8'
ADDR = ("127.0.0.1", 8080)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def handle_client(client:socket.socket):
    client.send(b"Hello, I'm from the server")
    msg = client.recv(2024).decode(FORMAT)
    print(msg)

# First estabilish the connection with the client
server.listen()
print(f"[LITSEN]Server is now listening on {ADDR}")
while True:
    conn, addr = server.accept()
    thread = threading.Thread(target=handle_client, args=(conn,))
    thread.start()
    print(f"[CONNECTION]Successfully connected with {conn}")


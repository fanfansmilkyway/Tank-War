import socket
import threading
import time

FORMAT = 'utf-8'
ADDR = ("127.0.0.1", 8080)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = [] # The lish which stores all the connected clients

# Sending Functions
def CREATE(client, tank_id:str, tank_model:str, spawn_coordinate:list):
    """
    Inform the client that a tank has been created
    """
    message = f"CREATE*/*{tank_id}+{tank_model}*/*{spawn_coordinate}"
    client.send(message.encode(FORMAT))

def MOVETO(client, tank_id:str, destination:list):
    """
    Inform the client that a tank moved to a certain location
    """
    message = f"MOVETO*/*{tank_id}*/*{destination}"
    client.send(message.encode(FORMAT))

def SHOOT(client, shooter_tank_id:str, target_tank_id:str):
    """
    Inform the client that a tank shot a shell to another
    """
    message = f"SHOOT*/*{shooter_tank_id}*/*{target_tank_id}"
    client.send(message.encode(FORMAT))

def DESTROYED(client, destroyed_tank_id:str):
    """
    Inform the client that a tank has been destroyed
    """
    message = f"DESTROYED*/*{destroyed_tank_id}"
    client.send(message.encode(FORMAT))

def QUIT(client):
    """
    Inform the server that the other client quited
    """
    message = "QUIT"
    client.sned(message.encode(FORMAT))

msg = ""

def handle_client(client:socket.socket):
    global msg
    while True:
        len_msg = client.recv(5).decode(FORMAT)
        if len_msg != "":
            try:
                int(len_msg)
            except ValueError:
                continue
            b_msg = client.recv(int(len_msg))
            msg = b_msg.decode(FORMAT)
            # Broadcast the message to other clients
            for conn in clients:
                if conn != client:
                    len_msg = "{:05d}".format(len(msg))
                    conn.send(len_msg.encode(FORMAT))
                    conn.send(b_msg)
            print(msg)
    

# First estabilish the connection with the client
server.listen()
print(f"[LITSEN]Server is now listening on {ADDR}")
while True:
    conn, addr = server.accept()
    clients.append(conn)
    thread = threading.Thread(target=handle_client, args=(conn,))
    thread.start()
    print(f"[CONNECTION]Successfully connected with {conn}")
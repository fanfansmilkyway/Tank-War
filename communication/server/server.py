import socket
import threading
import time

FORMAT = 'utf-8'
ADDR = ("127.0.0.1", 8080)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

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


def handle_client(client:socket.socket):
    time.sleep(0.5)
    client.send(b"MOVETO*/*B5*/*[500,500]")
    time.sleep(2)
    client.send(b"MOVETO*/*B5*/*[0,0]")
    

# First estabilish the connection with the client
server.listen()
print(f"[LITSEN]Server is now listening on {ADDR}")
while True:
    conn, addr = server.accept()
    thread = threading.Thread(target=handle_client, args=(conn,))
    thread.start()
    print(f"[CONNECTION]Successfully connected with {conn}")


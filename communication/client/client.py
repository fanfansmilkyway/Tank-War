import socket
import ast
import sys
import os

IP = '192.168.1.229'
PORT = 8081

FORMAT = 'utf-8'
ADDR = (IP, PORT) # Server IP

external_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(external_path)

from classes.Puppet_Tank import Puppet_Tank


class Communication_Client():
    def __init__(self, game):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect(ADDR)
        except ConnectionRefusedError:
            print('\033[31m', f"[ERROR]Unable to establish connection to the server. Please check your network status or the server's running status.")
            exit()
        print("[CONNECTION] Successfully connected with the server")
        self.game = game
        #self.CreatePuppetTank(id="B5", model="T34-76", team="BLUE", spawn_point=[300,250])
    
    def CreatePuppetTank(self, id, model, team, spawn_point):
        self.game.to_create_tank_id.append(id)
        self.game.to_create_tank_model.append(model)
        self.game.to_create_tank_team.append(team)
        self.game.to_create_tank_spawn_point.append(spawn_point)
        self.game.to_create_tank = True

    # Sending Functions
    def CREATE(self, tank_id:str, tank_model:str, spawn_coordinate:list):
        """
        Inform the server that a tank has been created
        """
        message = f"CREATE*/*{tank_id}+{tank_model}*/*{spawn_coordinate}"
        len_msg = "{:05d}".format(len(message))
        self.client.send(len_msg.encode(FORMAT))
        self.client.send(message.encode(FORMAT))

    def MOVETO(self, tank_id:str, destination:list):
        """
        Inform the server that a tank moved to a certain location
        """
        message = f"MOVETO*/*{tank_id}*/*{destination}"
        len_msg = "{:05d}".format(len(message))
        self.client.send(len_msg.encode(FORMAT))
        self.client.send(message.encode(FORMAT))

    def SHOOT(self, shooter_tank_id:str, target_tank_id:str):
        """
        Inform the server that a tank shot a shell to another tank.
        """
        message = f"SHOOT*/*{shooter_tank_id}*/*{target_tank_id}"
        len_msg = "{:05d}".format(len(message))
        self.client.send(len_msg.encode(FORMAT))
        self.client.send(message.encode(FORMAT))

    def DESTROYED(self, destroyed_tank_id:str):
        """
        Inform the server that one of our tanks has been destroyed
        """
        message = f"DESTROYED*/*{destroyed_tank_id}"
        len_msg = "{:05d}".format(len(message))
        self.client.send(len_msg.encode(FORMAT))
        self.client.send(message.encode(FORMAT))

    def QUIT(self):
        """
        Inform the server that the client quited
        """
        message = "QUIT"
        len_msg = "{:05d}".format(len(message))
        self.client.send(len_msg.encode(FORMAT))
        self.client.sned(message.encode(FORMAT))

    # Receiving Functions
    def Message_Parser(self, message:str):
        """
        Parses the message received, and executes.
        """
        # For detailed information, please see ./communication/notes.txt
        splitted_message = message.split("*/*")
        ACTION = splitted_message[0]
        if ACTION == "CREATE":
            OBJECT1 = splitted_message[1]
            splitted_OBJECT1 = OBJECT1.split("+")
            id = splitted_OBJECT1[0]
            model = splitted_OBJECT1[1]
            OBJECT2 = spawn_point = ast.literal_eval(splitted_message[2])
            #print(OBJECT1, OBJECT2)
            self.CreatePuppetTank(id=id, model=model, team="BLUE", spawn_point=spawn_point)

        if ACTION == "MOVETO":
            OBJECT1 = tank_id = splitted_message[1] # moved tank's id
            OBJECT2 = destination = ast.literal_eval(splitted_message[2]) # destination
            tank = self.game.tank_id[tank_id]
            tank.destination_x, tank.destination_y = destination[0], destination[1]
            tank.status = "MOVING"

    def run(self):
        while True:
            if self.game.GAMING == False:
                print("EXITED")
                sys.exit(0)
                break
            len_msg = self.client.recv(5).decode(FORMAT)
            if len_msg != "":
                try:
                    int(len_msg)
                except ValueError:
                    continue
                message = self.client.recv(int(len_msg)).decode(FORMAT)
            self.Message_Parser(message=message)
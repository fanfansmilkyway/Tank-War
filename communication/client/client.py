import socket
import ast
import sys
import os
import time

IP = '192.168.1.123'
PORT = 8081

FORMAT = 'utf-8'
ADDR = (IP, PORT) # Server IP

external_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(external_path)

class Communication_Client():
    def __init__(self, game):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("[CONNECTION] Successfully connected with the server")
        self.game = game
        self.message_cache = []
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

    def ROTATE(self, tank_id:str, rotated_angle:int):
        """
        Inform the server that one of our tanks rotated a certain angle
        """
        message = f"ROTATE*/*{tank_id}*/*{str(rotated_angle)}"
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
        self.client.send(message.encode(FORMAT))

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
            self.game.logger.info("Creating Puppet Tank")
            if id[0] == "R":
                self.CreatePuppetTank(id=id, model=model, team="RED", spawn_point=spawn_point)
            if id[0] == "B":
                self.CreatePuppetTank(id=id, model=model, team="BLUE", spawn_point=spawn_point)

        if ACTION == "MOVETO":
            OBJECT1 = tank_id = splitted_message[1] # moved tank's id
            OBJECT2 = destination = ast.literal_eval(splitted_message[2]) # destination
            tank = self.game.tank_id[tank_id]
            tank.destination_x, tank.destination_y = destination[0], destination[1]
            tank.status = "MOVING"

        if ACTION == "SHOOT":
            OBJECT1 = shooter_id = splitted_message[1]
            OBJECT2 = target_id = splitted_message[2]
            shooter = self.game.tank_id[shooter_id]
            target = self.game.tank_id[target_id]
            
            self.game.shooter_tank.append(shooter)
            self.game.target_tank.append(target)
            self.game.to_shoot = True

        if ACTION == "ROTATE":
            OBJECT1 = tank_id = splitted_message[1]
            OBJECT2 = rotated_angle = splitted_message[2]
            tank = self.game.tank_id[tank_id]

            self.game.rotated_tank.append(tank)
            self.game.rotated_angle.append(rotated_angle)
            self.game.to_rotate = True

        if ACTION == "TEAM":
            OBJECT1 = team_name = splitted_message[1]
            self.game.team = team_name

        if ACTION == "START":
            print("GAME START!")
            self.game.logger.info("Opponent Connected")
            self.game.IfGameStarted = True

        if ACTION == "DESTROYED":
            OBJECT1 = destroyed_tank_id = splitted_message[1]
            destroyed_tank = self.game.tank_id[destroyed_tank_id]
            destroyed_tank.destroyed()

    def run(self):
        try:
            self.client.connect(ADDR)
        except ConnectionRefusedError:
            print('\033[31m', f"[ERROR]Unable to establish connection to the server. Please check your network status or the server's running status.")
            exit()
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
                print(f"[Message Received] {message}")
                self.game.logger.info(f"Message Received: {message}")
            self.Message_Parser(message=message)
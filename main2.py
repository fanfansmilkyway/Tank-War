# Python 3.13.0
# Built-in Modules
from tkinter import *
import time
import sys
import logging
import threading
# Extension Modules
import playsound3
import waiting
# Customized Modules
from classes.Tank import Tank
from classes.Bunker import Bunker
from classes.Puppet_Tank import Puppet_Tank
from communication.client.client import Communication_Client
from global_functions import *


def CalculateRefreshRate(tick_time):
    """
    Calculate the Refresh Rate.
    """
    game.RefreshRate = round(1 / tick_time)
    game.ChangeFPSMessage(f"FPS: {game.RefreshRate}")

class Game:
    def __init__(self):
        # Initialize the canvas
        self.tk = Tk()
        self.tk.title("Tank War")
        self.canvas = Canvas(self.tk, background="white")
        self.tk.attributes('-fullscreen', True)
        self.canvas.pack(fill=BOTH, expand=True)
        self.canvas.update()
        self.canvas_width = self.canvas.winfo_screenwidth()
        self.canvas_height = self.canvas.winfo_screenheight()
        self.tk.protocol("WM_DELETE_WINDOW", self.end_game)

        self.message_box = Label(
            self.canvas, text="Attack...", background="grey")
        self.message_box.pack(side=LEFT, anchor="s")
        self.debug_message = Label(
            self.canvas, text="Debugging", background="grey")
        self.debug_message.pack(side=RIGHT, anchor="s")
        self.fps_message = Label(
            self.canvas, text="", background="grey")
        self.fps_message.pack(side=RIGHT, anchor="n")

        self.IfReadyFire = False
 
        self.selected_tanks = []

        self.canvas.bind_all("<KeyPress-a>", self.ReadyFire)
        self.canvas.bind_all("<ButtonPress-1>", self.GetLeftMousePosition)  # Left Click
        self.canvas.bind_all("<ButtonPress-2>", self.GetRightMousePosition)  # Right Click
        #self.canvas.bind_all("<KeyPress-f>", self.Forward)
        self.canvas.bind_all("<Escape>", self.CancelAll)
        self.canvas.bind_all("<KeyPress-e>", self.RotateClockwise)
        self.canvas.bind_all("<KeyPress-q>", self.RotateCounterClockwise)

        self.RefreshRate = 1
        self.tanks = []   # The list which stores all the tanks
        self.shells = []  # The list which stores all the shells
        self.teams = "RED"
        self.bunkers = [] # The list which stores all the bunkers

        self.tank_id = {} # The dictionary which stores all the tanks' id and its corresponding tank object

        self.client = Communication_Client(game=self)

        self.GAMING = True
        self.IfGameStarted = False # Whether the multi-player game've started or not(whehter the opponent has been ready).

        self.logger = logging.getLogger(__name__)
        logging.basicConfig(filename='./log/log.log', level=logging.INFO)

        self.logger.info(f"{time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())}:Game Launched")

        # Some tricky stuff
        self.to_create_tank = False
        self.to_create_tank_id = []
        self.to_create_tank_model = []
        self.to_create_tank_spawn_point = []
        self.to_create_tank_team = []

        self.to_shoot = False
        self.shooter_tank = []
        self.target_tank = []

        self.to_rotate = True
        self.rotated_tank = []
        self.rotated_angle = []

    def GetLeftMousePosition(self, event):
        """
        Get Mouse position when left click. And determine which and whether the tank is selected.
        """
        mouse_x = event.x
        mouse_y = event.y
        if self.IfReadyFire == False:
            for tank in self.tanks:
                bbox = self.canvas.bbox(tank.tank)  # Bounding Box
                if bbox[0] < mouse_x < bbox[2] and bbox[1] < mouse_y < bbox[3] and not isinstance(tank, Puppet_Tank):
                    if tank.IfSelected == False:
                        tank.IfSelected = True
                        self.selected_tanks.append(tank)
                    else:
                        tank.IfSelected = False
                        self.selected_tanks.remove(tank)
                else:
                    pass

        if self.IfReadyFire == True:
            target = None
            for tank in self.tanks:
                bbox = self.canvas.bbox(tank.tank)  # Bounding Box
                if bbox[0] < mouse_x < bbox[2] and bbox[1] < mouse_y < bbox[3]:
                    target = tank
            if target != None:
                for tank in self.selected_tanks:
                    tank.shoot(target)
                    self.client.SHOOT(tank.id, target.id)

            self.IfReadyFire = False

    def CreatePuppetTank(self):
        for index in range(len(self.to_create_tank_id)):
            puppet = Puppet_Tank(game=self, canvas=self.canvas, id=self.to_create_tank_id[index], tank_name=self.to_create_tank_model[index], spawn_point=self.to_create_tank_spawn_point[index], team=self.to_create_tank_team[index])
        self.to_create_tank = False
        self.to_create_tank_id.clear()
        self.to_create_tank_model.clear()
        self.to_create_tank_spawn_point.clear()
        self.to_create_tank_team.clear()
        return puppet
    
    def ShootPuppetShell(self):
        for index in range(len(self.shooter_tank)):
            self.shooter_tank[index].shoot(self.target_tank[index])
        self.to_shoot = False
        self.shooter_tank.clear()
        self.target_tank.clear()

    def PuppetRotation(self):
        for index in range(len(self.rotated_tank)):
            self.rotated_tank[index].rotate(int(self.rotated_angle[index]))
        self.to_rotate = False
        self.rotated_tank.clear()
        self.rotated_angle.clear()
    
    def RotateCounterClockwise(self, event):
        """
        Rotate the tank counterclockwise for 5 degrees
        """
        for tank in self.selected_tanks:
            tank.rotate(-5)
            self.client.ROTATE(tank.id, -5)

    def RotateClockwise(self, event):
        """
        Rotate the tank clockwise for 5 degress
        """
        for tank in self.selected_tanks:
            tank.rotate(5)
            self.client.ROTATE(tank.id, 5)

    def GetRightMousePosition(self, event):
        """
        Get Mouse position when right click. And command the tank(s) to go to the mouse's position.
        """
        mouse_x = event.x
        mouse_y = event.y
        # Determine whether the destination is inside the bunker(which is unreachable)
        for bunker in self.bunkers:
            if if_point_in_polygon((mouse_x,mouse_y), self.canvas.coords(bunker.bunker)) == True:
                error_message = Label(self.canvas, text="Unreachable Destination!", font=("Courier",12), background="red")
                error_message.place(x=mouse_x-40, y=mouse_y-3)
                self.tk.after(1000, error_message.destroy)
                playsound3.playsound("./mp3/Error.mp3", block=False)
                return
        for tank in self.selected_tanks:
            tank.destination_x = mouse_x
            tank.destination_y = mouse_y
            self.client.MOVETO(tank_id=tank.id, destination=[mouse_x, mouse_y])
            tank.status = "MOVING"

    def Forward(self, event):
        for tank in self.selected_tanks:
            tank.status = "GO_FORWARD"

    def ReadyFire(self, event):
        self.IfReadyFire = True

    def CancelAll(self, event):
        self.IfReadyFire = False
        for tank in self.tanks:
            tank.IfSelected = False
        self.selected_tanks.clear()

    def ChangeMessageBoxText(self, message):
        self.message_box.config(text=message)

    def ChangeDebugMessage(self, message):
        self.debug_message.config(text=message)
    
    def ChangeFPSMessage(self, message):
        self.fps_message.config(text=message)

    def refresh(self):
        """
        Game mainloop
        """
        for tank in self.tanks:
            tank.run()
        for shell in self.shells:
            shell.travel()
        if self.to_create_tank == True:
            self.CreatePuppetTank()
        if self.to_shoot == True:
            self.ShootPuppetShell()
        if self.to_rotate == True:
            self.PuppetRotation()

        game.tk.update()

    def end_game(self):
        self.GAMING = False
        sys.exit(0)

game = Game()

print(game.canvas_width, game.canvas_height)

Communication_Listen_Thread = threading.Thread(target=game.client.run, args=())
Communication_Listen_Thread.start()

print("IN WAITING")
waiting.wait(lambda:game.IfGameStarted) is True # Wait until the opponent connected
print("OUT WAITING")

"""
tank1 = Tank(game=game, id="R1", canvas=game.canvas, tank_name="PzIV H", spawn_point=[50, 50], team="RED")
tank2 = Tank(game=game, id="R2", canvas=game.canvas, tank_name="PzIII J", spawn_point=[50, 80], team="RED")
tank3 = Tank(game=game, id="R3", canvas=game.canvas, tank_name="T34-76", spawn_point=[50, 550], team="RED")
tank4 = Tank(game=game, id="R4", canvas=game.canvas, tank_name="Matilda II", spawn_point=[50, 600], team="RED")
"""
tank5 = Tank(game=game, id="B1", canvas=game.canvas, tank_name="PzIV H", spawn_point=[1000, 100], team="BLUE")
tank6 = Tank(game=game, id="B2", canvas=game.canvas, tank_name="PzIII J", spawn_point=[1000, 150], team="BLUE")
tank7 = Tank(game=game, id="B3", canvas=game.canvas, tank_name="Matilda II", spawn_point=[1000, 600], team="BLUE")
tank8 = Tank(game=game, id="B4", canvas=game.canvas, tank_name="BT-7", spawn_point=[1000, 700], team="BLUE")


bunker1 = Bunker(game=game, canvas=game.canvas, vertices=[400,400,300,300,300,400,400,450])
bunker2 = Bunker(game=game, canvas=game.canvas, vertices=[600,400,800,100,700,450,750,450])
bunker3 = Bunker(game=game, canvas=game.canvas, vertices=[800,900,600,500,700,400,800,450])

# Print canvas's width and height

while True:
    if game.GAMING == True and game.IfGameStarted == True:
        T1 = time.time()
        game.refresh()
        T2 = time.time()
        CalculateRefreshRate(T2-T1)
    if game.GAMING == False:
        break

sys.exit(0)
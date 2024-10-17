from tkinter import *
import math
import time
import sys

GAMING = True

# "Tank Name": [Attack, Armour, Speed]
TANK_DATA = {"T34":[50,50,2],
            "PzIII":[40,40,5],
            "PzIV":[50,50,3]}

tanks = [] # The list which stores all the tanks

class Game:
    def __init__(self):
        self.tk = Tk()
        self.tk.title("Tank War")
        self.canvas = Canvas(self.tk, background="white")
        self.tk.attributes('-fullscreen', True)
        self.canvas.pack(fill=BOTH, expand=True)
        self.canvas.update()
        self.canvas_width = self.canvas.winfo_screenwidth()
        self.canvas_height = self.canvas.winfo_screenheight()
        self.tk.protocol("WM_DELETE_WINDOW", self.end_game)
        self.message_box = Label(self.canvas, text="Attack...", background="grey")
        self.message_box.pack(side=LEFT, anchor="s")

        self.IfReadyFire = False

        self.canvas.bind_all("<KeyPress-a>", self.ReadyFire)
        self.canvas.bind_all("<ButtonPress-1>", self.GetLeftMousePosition) # Left Click
        self.canvas.bind_all("<ButtonPress-2>", self.GetRightMousePosition) # Right Click
        self.canvas.bind_all("<Escape>", self.CancelAll)

    def GetLeftMousePosition(self, event):
        """
        Get Mouse position when left click. And determine which and whether the tank is selected.
        """
        mouse_x = event.x
        mouse_y = event.y
        if self.IfReadyFire == False:
            for tank in tanks:
                bbox = self.canvas.bbox(tank.tank) # Bounding Box
                if bbox[0] < mouse_x < bbox[2] and bbox[1] < mouse_y < bbox[3]:
                    if tank.IfSelected == False:
                        tank.IfSelected = True
                    else:
                        tank.IfSelected = False
                else:
                    pass
        
        if self.IfReadyFire == True:
            tanks_ready_fire = []
            target = None
            for tank in tanks:
                if tank.IfSelected == True:
                    tanks_ready_fire.append(tank)
                bbox = self.canvas.bbox(tank.tank) # Bounding Box
                if bbox[0] < mouse_x < bbox[2] and bbox[1] < mouse_y < bbox[3]:
                    target = tank
            if target != None:
                name_list = []
                for tank in tanks_ready_fire:
                    name_list.append(tank.tank_name)
                self.ChangeMessageBoxText(f"{name_list} --> {target.tank_name}")
            self.IfReadyFire = False

    def GetRightMousePosition(self, event):
        """
        Get Mouse position when right click. And command the tank(s) to go to the mouse's position.
        """
        mouse_x = event.x
        mouse_y = event.y
        for tank in tanks:
            if tank.IfSelected == True:
                tank.destination_x = mouse_x
                tank.destination_y = mouse_y
                tank.status = "MOVING"

    def ReadyFire(self, event):
        self.IfReadyFire = True            

    def CancelAll(self, event):
        self.IfReadyFire = False
        for tank in tanks:
            tank.IfSelected = False

    def ChangeMessageBoxText(self, message):
        self.message_box.config(text=message)

    def run(self):
        """
        Game mainloop
        """
        for tank in tanks:
            tank.run()
        
    def end_game(self):
        global GAMING
        GAMING = False

class Tank:
    def __init__(self, canvas:Canvas, tank_name:str, spawn_point:list=[100,100]):
        tanks.append(self)
        self.tank_name = tank_name
        try:
            self.capability = TANK_DATA[self.tank_name]
        except KeyError:
            print(f"[ERROR] Unknown tank type: {self.tank_name}")
            exit()
        self.speed = self.capability[2]
        self.canvas = canvas
        self.spawn_point = spawn_point
        # self.tank is the rectangle part of the tank. And self.tank_text shows above the rectangle, labels what the tank is.
        self.tank = self.canvas.create_rectangle(self.spawn_point[0]-12, self.spawn_point[1]-9, self.spawn_point[0]+12, self.spawn_point[1]+9, outline="red", fill='white')
        self.tank_text = self.canvas.create_text(self.spawn_point[0], self.spawn_point[1]-18, fill="black", text=self.tank_name, font=("Courier", "14"))
        self.previous_mouse_position = []
        self.destination_x = 0
        self.destination_y = 0
        # For better calculating speed
        self.previous_destination_x = -1 # -1 means no destination
        self.previous_destination_y = -1
        self.toward_x = 0
        self.toward_y = 0
        self.NumberOfMoves = 0

        self.status = "IDLE" # Status are: "IDLE", "MOVING"
        self.IfSelected = False

    def GetCurrentCoordinate(self):
        """
        Return current coordinate(the centre point of the tank)
        """
        current_coordinate = self.canvas.coords(self.tank)
        current_x = current_coordinate[0]+20
        current_y = current_coordinate[1]+15
        return current_x, current_y

    def TowardDestination(self, destination_x, destination_y):
        """
        About the value of this function returns:
        0: No destination / Movement Completed
        1: Movement not completed(now moving toward the destination)
        """
        current_x, current_y = self.GetCurrentCoordinate()
        if destination_x == current_x and destination_y == current_y:
            return 0  # Already at the destination
        if destination_x != self.previous_destination_x and destination_y != self.previous_destination_y:
            if current_y != destination_y:
                CalculationVar = (destination_x-current_x) / (destination_y-current_y)
                distance = math.sqrt((destination_x-current_x)**2 + (destination_y-current_y)**2)
                self.NumberOfMoves = round(distance / self.speed)
                self.toward_y = self.speed / math.sqrt(CalculationVar**2 + 1)
                self.toward_x = abs(CalculationVar * self.toward_y)
                if destination_y - current_y < 0:
                    self.toward_y = -self.toward_y
                if destination_x - current_x < 0:
                    self.toward_x = -self.toward_x
            
            if current_y == destination_y: # Prevent DividedByZero Error in CalculationVar
                if destination_x - current_x < 0:
                    self.toward_x = -self.speed
                if destination_x - current_x > 0:
                    self.toward_x = self.speed
                distance = abs(destination_x - current_x)
                self.NumberOfMoves = round(distance / self.speed)
                self.toward_y = 0

            self.previous_destination_x = destination_x
            self.previous_destination_y = destination_y

        if destination_x == -1 or destination_y == -1 or self.NumberOfMoves == 0: # No destination
            self.status = "IDLE"
            return 0

        if destination_x == self.previous_destination_x and destination_y == self.previous_destination_y:
            if self.NumberOfMoves <= 0:
                self.previous_destination_x = -1 # -1 means no destination
                self.previous_destination_y = -1
                self.status = "IDLE"
                return 0
            if self.NumberOfMoves > 0:
                self.canvas.move(self.tank, self.toward_x, self.toward_y)
                self.canvas.move(self.tank_text, self.toward_x, self.toward_y)
                self.canvas.update()
                self.NumberOfMoves -= 1
                self.status = "MOVING"
                return 1

    def run(self):
        if self.IfSelected == False:
            self.canvas.itemconfig(self.tank, fill="#ffffff")
        if self.IfSelected == True:
            self.canvas.itemconfig(self.tank, fill="#ff0000")
        if self.status == "IDLE":
            pass
        if self.status == "MOVING":
            self.TowardDestination(self.destination_x, self.destination_y)

game = Game()
tank1 = Tank(canvas=game.canvas, tank_name="T34", spawn_point=[500,500])
tank2 = Tank(canvas=game.canvas, tank_name="PzIII", spawn_point=[500,200])
tank3 = Tank(canvas=game.canvas, tank_name="PzIV", spawn_point=[500,700])
print(game.canvas_width, game.canvas_height)

while True:
    if GAMING == True:
        game.run()
        game.tk.update_idletasks()
        game.tk.update()
    if GAMING == False:
        break

sys.exit()
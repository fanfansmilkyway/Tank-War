from tkinter import *
import math
import time
import sys

GAMING = True

# "Tank Name": [Attack, Armour, Speed]
TANK_DATA = {"T34":[50,50,2],
            "PzIII":[40,40,5]}

tanks = []

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

        self.canvas.bind_all("<ButtonPress-1>", self.GetLeftMousePosition) # Left Click
        self.canvas.bind_all("<ButtonPress-2>", self.GetRightMousePosition) # Right Click
        self.canvas.bind_all("<Escape>", self.CancelAllSelect)

    def GetLeftMousePosition(self, event):
        """
        Get Mouse position when left click. And determine which and whether the tank is selected.
        """
        mouse_x = event.x
        mouse_y = event.y
        for tank in tanks:
            bbox = self.canvas.bbox(tank.tank) # Bounding Box
            if bbox[0] < mouse_x < bbox[2] and bbox[1] < mouse_y < bbox[3]:
                if tank.IfSelected == False:
                    tank.IfSelected = True
                else:
                    tank.IfSelected = False
            else:
                pass

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

    def CancelAllSelect(self, event):
        for tank in tanks:
            tank.IfSelected = False

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
        self.tank = self.canvas.create_text(self.spawn_point[0], self.spawn_point[1], fill="black", text=self.tank_name)
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

    def TowardDestination(self, destination_x, destination_y):
        """
        About the value of this function returns:
        0: No destination / Movement Completed
        1: Movement not completed(now moving toward the destination)
        """
        current_coordinate = self.canvas.coords(self.tank)
        current_x = current_coordinate[0]
        current_y = current_coordinate[1]
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
                self.canvas.update()
                self.NumberOfMoves -= 1
                self.status = "MOVING"
                return 1

    def run(self):
        if self.IfSelected == False:
            self.canvas.itemconfig(self.tank, fill="#000000")
        if self.IfSelected == True:
            self.canvas.itemconfig(self.tank, fill="#ff0000")
        if self.status == "IDLE":
            pass
        if self.status == "MOVING":
            self.TowardDestination(self.destination_x, self.destination_y)

game = Game()
tank1 = Tank(canvas=game.canvas, tank_name="T34", spawn_point=[500,500])
tank2 = Tank(canvas=game.canvas, tank_name="PzIII", spawn_point=[500,200])
print(game.canvas_width, game.canvas_height)

while True:
    if GAMING == True:
        game.run()
        game.tk.update_idletasks()
        game.tk.update()
        time.sleep(0.01)
    if GAMING == False:
        break

sys.exit()
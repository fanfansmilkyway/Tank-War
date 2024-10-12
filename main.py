from tkinter import *
import math
import time
import sys

GAMING = True

# "Tank Name": [Attack, Armour, Speed]
TANK_DATA = {"T34":[50,50,2],
            "PanzerIII":[40,40,0.4]}

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

    def end_game(self):
        global GAMING
        GAMING = False

class Tank:
    def __init__(self, canvas:Canvas, tank_name:str):
        self.tank_name = tank_name
        try:
            self.capability = TANK_DATA[self.tank_name]
        except KeyError:
            print(f"[ERROR] Unknown tank type: {self.tank_name}")
            exit()
        self.speed = self.capability[2]
        self.canvas = canvas
        self.tank = self.canvas.create_text(300, 200, fill="black", text=self.tank_name)
        self.previous_mouse_position = []
        # For better calculating speed
        self.previous_destination_x = -1 # -1 means no destination
        self.previous_destination_y = -1
        self.toward_x = 0
        self.toward_y = 0
        self.NumberOfMoves = 0

        self.canvas.bind_all("<ButtonPress-1>", self.TowardMousePosition)
        self.status = "STOP" # Status are: "STOP", "MOVING"


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
            print("At destination")
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
            return 0

        if destination_x == self.previous_destination_x and destination_y == self.previous_destination_y:
            if self.NumberOfMoves <= 0:
                self.previous_destination_x = -1 # -1 means no destination
                self.previous_destination_y = -1
                self.status = "STOP"
                return 0
            if self.NumberOfMoves > 0:
                self.canvas.move(self.tank, self.toward_x, self.toward_y)
                self.canvas.update()
                self.NumberOfMoves -= 1
                return 1

    def TowardMousePosition(self, event):
        """
        Get the mouse's coordinate when left click.
        """
        self.mouse_x = event.x
        self.mouse_y = event.y
        self.status = "MOVING"

    def run(self):
        if self.status == "STOP":
            pass
        if self.status == "MOVING":
            self.TowardDestination(self.mouse_x, self.mouse_y)

game = Game()
T34 = Tank(canvas=game.canvas, tank_name="T34")
print(game.canvas_width, game.canvas_height)

while True:
    if GAMING == True:
        T34.run()
        game.tk.update_idletasks()
        game.tk.update()
        time.sleep(0.01)
    if GAMING == False:
        break

sys.exit()
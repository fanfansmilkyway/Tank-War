from tkinter import *
import math
import time

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
        # For better calculating speed
        self.previous_destination_x = -1 # -1 means no destination
        self.previous_destination_y = -1
        self.toward_x = 0
        self.toward_y = 0
        self.NumberOfMoves = 0

    def TowardDestination(self, destination_x, destination_y):
        if destination_x != self.previous_destination_x and destination_y != self.previous_destination_y:
            current_coordinate = self.canvas.coords(self.tank)
            current_x = current_coordinate[0]
            current_y = current_coordinate[1]
            CalculationVar = (destination_x-current_x) / (destination_y-current_y)
            distance = math.sqrt((destination_x-current_x)**2 + (destination_y-current_y)**2)
            self.NumberOfMoves = round(distance / self.speed)
            print(self.NumberOfMoves)
            self.toward_y = self.speed / math.sqrt(CalculationVar*CalculationVar + 1)
            self.toward_x = CalculationVar * self.toward_y
            print(self.toward_x, self.toward_y)
            if destination_y - current_y < 0:
                self.toward_y = -self.toward_y
            if destination_x - current_x < 0:
                self.toward_x = -self.toward_x
            self.canvas.move(self.tank, self.toward_x, self.toward_y)
            self.NumberOfMoves -= 1
            self.previous_destination_x = destination_x
            self.previous_destination_y = destination_y

        if destination_x == -1 or destination_y == -1 or self.NumberOfMoves == 0: # No destination
            print("No destination")
            return 0

        if destination_x == self.previous_destination_x and destination_y == self.previous_destination_y:
            if self.NumberOfMoves <= 0:
                self.previous_destination_x = -1 # -1 means no destination
                self.previous_destination_y = -1
            if self.NumberOfMoves > 0:
                print(self.toward_x, self.toward_y)
                self.canvas.move(self.tank, self.toward_x, self.toward_y)
                self.canvas.update()
                self.NumberOfMoves -= 1
        

game = Game()
T34 = Tank(canvas=game.canvas, tank_name="T34")

print(game.canvas_width, game.canvas_height)

while True:
    T34.TowardDestination(400,400)
    game.tk.update_idletasks()
    game.tk.update()
    time.sleep(0.01)
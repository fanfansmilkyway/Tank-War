from tkinter import *
import time

# "Tank Name": [Attack, Armour, Speed]
TANK_DATA = {"T34":[50,50,0.3],
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

    def draw(self):
        self.canvas.move(self.tank, self.speed, 0)
        self.canvas.update()


game = Game()
T34 = Tank(canvas=game.canvas, tank_name="PanzerIII")

print(game.canvas_width, game.canvas_height)

while True:
    T34.draw()
    game.tk.update_idletasks()
    game.tk.update()
    time.sleep(0.01)
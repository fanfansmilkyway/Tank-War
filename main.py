from tkinter import *
import time
import sys
import playsound3
from classes.Tank import Tank
from classes.Bunker import Bunker
import global_variables as g_val
from global_functions import *

"""
The RefreshRate is dynamically adjusted, depending on the performance of the console.
The term "tick" means 100/s, "tick" is not associated with the RefreshRate.
"""

GAMING = True 

def CalculateRefreshRate(tick_time):
    """
    Calculate the Refresh Rate.
    """
    g_val.RefreshRate = round(1 / tick_time)
    game.ChangeFPSMessage(f"FPS: {g_val.RefreshRate}")

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
        self.canvas.bind_all("<Escape>", self.CancelAll)
        self.canvas.bind_all("<KeyPress-e>", self.RotateClockwise)
        self.canvas.bind_all("<KeyPress-q>", self.RotateCounterClockwise)

    def GetLeftMousePosition(self, event):
        """
        Get Mouse position when left click. And determine which and whether the tank is selected.
        """
        mouse_x = event.x
        mouse_y = event.y
        if self.IfReadyFire == False:
            for tank in g_val.tanks:
                bbox = self.canvas.bbox(tank.tank)  # Bounding Box
                if bbox[0] < mouse_x < bbox[2] and bbox[1] < mouse_y < bbox[3]:
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
            for tank in g_val.tanks:
                bbox = self.canvas.bbox(tank.tank)  # Bounding Box
                if bbox[0] < mouse_x < bbox[2] and bbox[1] < mouse_y < bbox[3]:
                    target = tank
            if target != None:
                name_list = []
                for tank in self.selected_tanks:
                    tank.shoot(target)
                    name_list.append(tank.tank_name)

            self.IfReadyFire = False

    def RotateCounterClockwise(self, event):
        """
        Rotate the tank counterclockwise for 5 degrees
        """
        for tank in self.selected_tanks:
            tank.rotate(-5)

    def RotateClockwise(self, event):
        """
        Rotate the tank clockwise for 5 degress
        """
        for tank in self.selected_tanks:
            tank.rotate(5)

    def GetRightMousePosition(self, event):
        """
        Get Mouse position when right click. And command the tank(s) to go to the mouse's position.
        """
        mouse_x = event.x
        mouse_y = event.y
        # Determine whether the destination is inside the bunker(which is unreachable)
        for bunker in g_val.bunkers:
            if if_point_in_polygon((mouse_x,mouse_y), self.canvas.coords(bunker.bunker)) == True:
                error_message = Label(self.canvas, text="Unreachable Destination!", font=("Courier",12), background="red")
                error_message.place(x=mouse_x-40, y=mouse_y-3)
                self.tk.after(1000, error_message.destroy)
                playsound3.playsound("./mp3/Error.mp3", block=False)
                return
        for tank in self.selected_tanks:
            tank.destination_x = mouse_x
            tank.destination_y = mouse_y
            tank.status = "MOVING"

    def ReadyFire(self, event):
        self.IfReadyFire = True

    def CancelAll(self, event):
        self.IfReadyFire = False
        for tank in g_val.tanks:
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
        for tank in g_val.tanks:
            tank.run()
        for shell in g_val.shells:
            shell.travel()
        game.tk.update()

    def end_game(self):
        global GAMING
        GAMING = False

game = Game()
tank1 = Tank(game=game, canvas=game.canvas, tank_name="PzIV H", spawn_point=[50, 50], team="RED")
tank2 = Tank(game=game, canvas=game.canvas, tank_name="PzIII J", spawn_point=[50, 80], team="RED")
tank3 = Tank(game=game, canvas=game.canvas, tank_name="T34-76", spawn_point=[50, 550], team="RED")
tank4 = Tank(game=game, canvas=game.canvas, tank_name="Matilda II", spawn_point=[50, 600], team="RED")
tank5 = Tank(game=game, canvas=game.canvas, tank_name="PzIV H", spawn_point=[1300, 100], team="BLUE")
tank6 = Tank(game=game, canvas=game.canvas, tank_name="PzIII J", spawn_point=[1300, 150], team="BLUE")
tank7 = Tank(game=game, canvas=game.canvas, tank_name="Matilda II", spawn_point=[1300, 600], team="BLUE")
tank8 = Tank(game=game, canvas=game.canvas, tank_name="BT-7", spawn_point=[1300, 700], team="BLUE")

bunker1 = Bunker(canvas=game.canvas, vertices=[400,400,300,300,300,400,400,450])
bunker2 = Bunker(canvas=game.canvas, vertices=[600,400,800,100,700,450,750,450])
bunker3 = Bunker(canvas=game.canvas, vertices=[800,900,600,500,700,400,800,450])

# Print canvas's width and height
print(game.canvas_width, game.canvas_height)

while True:
    if GAMING == True:
        T1 = time.time()
        game.refresh()
        T2 = time.time()
        CalculateRefreshRate(T2-T1)
    if GAMING == False:
        break

sys.exit()
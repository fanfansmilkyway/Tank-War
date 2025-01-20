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
import Tank_Data as tank_data


# Game Settings
BGM = False

def CalculateRefreshRate(tick_time):
    """
    Calculate the Refresh Rate.
    """
    game.RefreshRate = round(1 / tick_time)
    game.ChangeFPSMessage(f"FPS: {game.RefreshRate}")

def BGM_Loop():
    while True:
        playsound3.playsound("mp3/BGM -- Battle Start.mp3", block=True)

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
        self.puppet_tanks = [] # The list which stores all the puppet tanks
        self.shells = []  # The list which stores all the shells
        self.team = "RED"
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
                if bbox == None:
                    continue
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
            if self.to_create_tank_id[index][0] != self.team[0]:
                puppet = Puppet_Tank(game=self, canvas=self.canvas, id=self.to_create_tank_id[index], tank_name=self.to_create_tank_model[index], spawn_point=self.to_create_tank_spawn_point[index], team=self.to_create_tank_team[index])
            if self.to_create_tank_id[index][0] == self.team[0]:
                tank = Tank(game=self, canvas=self.canvas, id=self.to_create_tank_id[index], tank_name=self.to_create_tank_model[index], spawn_point=self.to_create_tank_spawn_point[index], team=self.to_create_tank_team[index])
        self.to_create_tank = False
        self.to_create_tank_id.clear()
        self.to_create_tank_model.clear()
        self.to_create_tank_spawn_point.clear()
        self.to_create_tank_team.clear()

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
        print("Game Ended")
        self.GAMING = False
        self.canvas.destroy()
        sys.exit(0)

game = Game()

print(game.canvas_width, game.canvas_height)

IfSelecting = True
chosen_tanks = []
def Select_Tanks():
    def submit_tank():
        if len(chosen_tanks) >= 10:
            reach_tank_limit_warning = Label(text="You've reached the tank limit of 10! You cannot add more tanks.", font=("Tohoma", 12), fg="red", background="white")
            reach_tank_limit_warning.place(relx=.5, rely=.16, anchor="s")
            game.tk.after(3000, reach_tank_limit_warning.destroy)
            playsound3.playsound("mp3/Error.mp3", block=False)
            return
        tank = selected_tank.get()
        chosen_tanks.append(tank)
        chosen_tanks_list.insert(END, tank)
        game.tk.update()

    def finish_selecting():
        global IfSelecting
        print(chosen_tanks)
        title.destroy()
        choice_box.destroy()
        submit_button.destroy()
        finish_button.destroy()
        description_text.destroy()
        tank_model_label.destroy()
        label1.destroy()
        tank_capacity_text.destroy()
        chosen_tanks_list.destroy()
        label2.destroy()
        clear_list_button.destroy()
        IfSelecting = False

    def modify_capacity_description(tank_model):
        description = """Firepower(Penetration):\n"""
        firepower_list = tank_data.TANK_CAPABILITY[tank_model][0]
        description = description + f"0m:    {firepower_list[0]}mm\n"
        description = description + f"100m:  {firepower_list[1]}mm\n"
        description = description + f"300m:  {firepower_list[2]}mm\n"
        description = description + f"500m:  {firepower_list[3]}mm\n"
        description = description + f"1000m: {firepower_list[4]}mm\n"
        description = description + f"1500m: {firepower_list[5]}mm\n"
        description = description + f"2000m: {firepower_list[6]}mm\n"
        description = description + f"3000m: {firepower_list[7]}mm\n\n"
        armour_list = tank_data.TANK_CAPABILITY[tank_model][1]
        description = description + "Armour:\n"
        description = description + f"Front: {armour_list[0]}mm\n"
        description = description + f"Side:  {armour_list[1]}mm\n"
        description = description + f"Rear:  {armour_list[2]}mm\n\n"
        description = description + "Max Speed:\n"
        description = description + f"{round(tank_data.TANK_CAPABILITY[tank_model][2]*18/5,1)}km/h\n\n"
        description = description + "Reloading Time:\n"
        description = description + f"{tank_data.TANK_CAPABILITY[tank_model][3]}s"

        tank_capacity_text.delete("1.0", END)
        tank_capacity_text.insert(END, description)

    def change_tank_description(*args):
        tank = selected_tank.get()
        description_text.delete("1.0", END)
        description_text.insert(END, tank_data.TANK_DESCRIPTION[tank])
        modify_capacity_description(tank_model=tank)
        tank_model_label.config(text=tank)

    def clear_list(*args):
        chosen_tanks.clear()
        chosen_tanks_list.delete(0, END)

    title = Label(game.tk, text="Choose Your Tanks, Commander!", font=("Courier", 40), fg="black", background="white")
    title.place(relx=.5, rely=.01, anchor='n')
    choices = tank_data.ALL_TANKS
    selected_tank = StringVar(game.tk)
    selected_tank.set("PzIV H")
    choice_box = OptionMenu(game.tk, selected_tank, *choices)
    selected_tank.trace_add('write', change_tank_description)  
    choice_box.place(relx=.5, rely=.19, anchor="e")
    submit_button = Button(game.tk, text="Enlist!", command=submit_tank)
    submit_button.place(relx=.5, rely=.19, anchor="w")
    finish_button = Button(game.tk, text="Ready for Battle!", command=finish_selecting)
    finish_button.place(relx=.5, rely=.21, anchor='n')
    description_text = Text(game.tk, font=("Courier", 14), background="white", fg="black", width=70, wrap=WORD)
    description_text.insert(END, chars=tank_data.TANK_DESCRIPTION["PzIV H"])
    description_text.place(relx=.4, rely=.19, anchor="ne")
    tank_model_label = Label(game.tk, background="white", fg="black", font=("Tahoma", 20), text="PzIV H")
    tank_model_label.place(relx=.2, rely=.19, anchor="s")

    label1 = Label(game.tk, text="Capacity", font=("Tahoma", 20), fg="black", background="white")
    label1.place(relx=.7, rely=.19, anchor="s")
    tank_capacity_text = Text(game.tk, font=("Courier", 14), background="white", fg="black", width=40, height=21)
    tank_capacity_text.place(relx=.6, rely=0.19, anchor="nw")
    modify_capacity_description(tank_model="PzIV H")

    label2 = Label(game.tk, text="Enlisted Tanks", font=('Tahoma',18), fg="black", background="white")
    label2.place(relx=.5, rely=.45, anchor='s')
    chosen_tanks_list = Listbox(game.tk, background="white", fg="black", height=11)
    chosen_tanks_list.place(relx=.5, rely=.45, anchor="n")
    clear_list_button = Button(game.tk, text="Clear", background="white", fg="black", command=clear_list)
    clear_list_button.place(relx=.5, rely=.70, anchor='n')

    while IfSelecting==True:
        game.tk.update()

if BGM == True:
    BGM_Thread = threading.Thread(target=BGM_Loop, args=())
    BGM_Thread.start()

Select_Tanks()
print("IN WAITING FOR SELECTING")
waiting.wait(lambda:not IfSelecting) is True
print("OUT WAITING FOR SELECTING TANKS")

Communication_Thread = threading.Thread(target=game.client.run, args=())
Communication_Thread.start()

print("IN WAITING FOR OPPONENT")
waiting_msg = Label(game.tk, text="Waiting for the opponent...", font=("Impact", 38), fg="black", background="white")
waiting_msg.place(relx=.5, rely=.5, anchor="center")
game.tk.update()
waiting.wait(lambda:game.IfGameStarted) is True # Wait until the opponent connected
waiting_msg.destroy()
print("OUT WAITING FOR OPPONENT")

for index in range(len(chosen_tanks)):
    model = chosen_tanks[index]
    id = f"{game.team[0]}{index+1}"
    game.to_create_tank_model.append(model)
    game.to_create_tank_id.append(id)
    game.to_create_tank_team.append(game.team)
    if game.team == "RED":
        spawn_point = [50, 300+50*index]
    if game.team == "BLUE":
        spawn_point = [1000, 300+50*index]
    game.to_create_tank_spawn_point.append(spawn_point)
    game.client.CREATE(tank_id=f"{game.team[0]}{index+1}", tank_model=chosen_tanks[index], spawn_coordinate=spawn_point)

game.to_create_tank = True

bunker1 = Bunker(game=game, canvas=game.canvas, vertices=[400,400,300,300,300,400,400,450])
bunker2 = Bunker(game=game, canvas=game.canvas, vertices=[600,400,800,100,700,450,750,450])
bunker3 = Bunker(game=game, canvas=game.canvas, vertices=[800,900,600,500,700,400,800,450])

team_msg = Label(game.tk, text=f"You are the {game.team} team!", fg="black", font=("Courier", 18), background="white", border=0, padx=0, pady=0)
team_msg.place(relx=.0, rely=.0, anchor="nw")
game.tk.update()
game.tk.after(10000, team_msg.destroy)

while True:
    if game.GAMING == True and game.IfGameStarted == True:
        T1 = time.time()
        game.refresh()
        T2 = time.time()
        CalculateRefreshRate(T2-T1)
    if game.GAMING == False:
        break

sys.exit(0)
from tkinter import *
import math
import random
import time
import sys
import playsound3

GAMING = True
RefreshRate = 100 
"""
The RefreshRate is dynamically adjusted, depending on the performance of the console.
The term "tick" means 100/s, "tick" is not associated with the RefreshRate.
"""

# "Tank Name": [Attack(0m, 100m, 300m, 500m, 1000m, 1500m, 2000m, 3000m)mm, Relative Armor(front, side, rear), Speed(pixel / sec)]
TANK_DATA = {"T34": [[100, 85, 80, 73, 68, 62, 57, 45], [52, 52, 46], 9.7],
             "PzIII J": [[60, 55, 50, 57, 47, 28, 21, 15, 5], [50, 30, 45], 8.4],
             "PzIV H": [[140, 135, 130, 123, 109, 97, 86, 68], [80, 30, 20], 5.55]}

tanks = []   # The list which stores all the tanks
shells = []  # The list which stores all the shells
teams = ["RED", "BLUE"]   # The list which stores all the teams
bunkers = [] # The list which stores all the bunkers

BenchMarkTime = time.time()


def cross_product(x1, y1, x2, y2, x3, y3):
    return (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)

def is_intersect(A:tuple, B:tuple, C:tuple, D:tuple):
    """
    Determine whether two line segment intersects(AB, CD)
    """
    d1 = cross_product(C[0], C[1], D[0], D[1], A[0], A[1])
    d2 = cross_product(C[0], C[1], D[0], D[1], B[0], B[1])
    d3 = cross_product(A[0], A[1], B[0], B[1], C[0], C[1])
    d4 = cross_product(A[0], A[1], B[0], B[1], D[0], D[1])

    if d1 * d2 < 0 and d3 * d4 < 0:
        return True
    return False

def if_point_in_polygon(point:tuple, polygon):
    """
    To determine whether a point is in a polygon. True for the point is in the polygon. False for the point is not in it.
    """
    Intersection_Count = 0
    RAY_END = (30000, point[1])
    vertices = game.canvas.coords(polygon)
    vertices = [vertices[i:i+2] for i in range(0, len(vertices), 2)]
    SIDES = []
    index = 0
    for vertice in vertices:
        if index == len(vertices) - 1:
            SIDES.append([(vertices[0][0],vertices[0][1]), (vertices[index][0], vertices[index][1])])
        else:
            SIDES.append([(vertice[0],vertice[1]), (vertices[index+1][0], vertices[index+1][1])])
        index += 1

    for side in SIDES:
        if is_intersect(point, RAY_END, side[0], side[1]):
            Intersection_Count += 1
    
    if Intersection_Count % 2 == 0:
        return False
    else:
        return True

def FrequencyGenerator(frequency=1, bias=0.01):
    global BenchMarkTime, IfTriggered
    current_time = time.time()
    if current_time - BenchMarkTime < (frequency + bias) and current_time - BenchMarkTime > (frequency - bias):
        BenchMarkTime = current_time
        IfTriggered = True
        return True
    else:
        IfTriggered = False
        return False
    
def TickDynamicAdjustment(tick_time):
    """
    Adjust tick sleep time in order to preserve the refresh rate at certain frequency.
    """
    global RefreshRate
    RefreshRate = round(1 / tick_time)
    game.ChangeFPSMessage(f"FPS: {RefreshRate}")

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
        self.canvas.bind_all(
            "<ButtonPress-1>", self.GetLeftMousePosition)  # Left Click
        self.canvas.bind_all(
            "<ButtonPress-2>", self.GetRightMousePosition)  # Right Click
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
            for tank in tanks:
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
            for tank in tanks:
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
        for tank in self.selected_tanks:
            tank.destination_x = mouse_x
            tank.destination_y = mouse_y
            tank.status = "MOVING"

    def ReadyFire(self, event):
        self.IfReadyFire = True

    def CancelAll(self, event):
        self.IfReadyFire = False
        for tank in tanks:
            tank.IfSelected = False
        self.selected_tanks.clear()

    def ChangeMessageBoxText(self, message):
        self.message_box.config(text=message)

    def ChangeDebugMessage(self, message):
        self.debug_message.config(text=message)
    
    def ChangeFPSMessage(self, message):
        self.fps_message.config(text=message)

    def run(self):
        """
        Game mainloop
        """
        for tank in tanks:
            tank.run()
        for shell in shells:
            shell.travel()

    def end_game(self):
        global GAMING
        GAMING = False


class Tank:
    def __init__(self, canvas: Canvas, tank_name: str, team:str, spawn_point: list = [100, 100]):
        tanks.append(self)
        self.tank_name = tank_name
        self.team = team  # team name represents its color
        #self.team = team
        try:
            self.capability = TANK_DATA[self.tank_name]
        except KeyError:
            print(f"[ERROR] Unknown tank type: {self.tank_name}")
            exit()
        self.speed = self.capability[2] # pix/sec
        self.canvas = canvas
        self.spawn_point = spawn_point
        # self.tank is the rectangle part of the tank. And self.tank_text shows above the rectangle, labels what the tank is.
        self.vertices = [self.spawn_point[0]-8, self.spawn_point[1]-6, self.spawn_point[0]+8, self.spawn_point[1] -
                         6, self.spawn_point[0]+8, self.spawn_point[1]+6, self.spawn_point[0]-8, self.spawn_point[1]+6]
        self.tank = self.canvas.create_polygon(
            self.vertices, outline=self.team, fill="white")
        self.tank_text = self.canvas.create_text(
            self.spawn_point[0], self.spawn_point[1]-14, fill="black", text=self.tank_name, font=("Courier", "10"))
        self.direction_label = self.canvas.create_line(
            self.spawn_point[0], self.spawn_point[1], self.spawn_point[0]+20, self.spawn_point[1], arrow=LAST, fill="BLACK")
        self.direction_point = [self.spawn_point[0]+20, self.spawn_point[1]]
        self.previous_mouse_position = []
        self.destination_x = 0
        self.destination_y = 0
        # For better calculating speed
        self.previous_destination_x = -1  # -1 means no destination
        self.previous_destination_y = -1
        self.toward_x = 0
        self.toward_y = 0
        self.NumberOfMoves = 0

        self.status = "IDLE"  # Status are: "IDLE", "MOVING", "DESTROYED"
        self.IfSelected = False

    def GetCentreCoordinate(self, target=None):
        """
        Return current coordinate(the centre point of the tank). Or get other tank's coordinate.
        """
        if target == None:
            target = self
        current_coordinate = self.canvas.coords(target.tank)
        x1, y1, x2, y2, x3, y3, x4, y4 = current_coordinate
        # Solve linear functions
        k1 = (y1-y3) / (x1-x3)
        b1 = y1 - x1*k1
        k2 = (y2-y4) / (x2-x4)
        b2 = y2 - x2*k2
        # Get the intersection point of them(the center point)
        centre_x = (b2-b1) / (k1-k2)
        centre_y = k1*centre_x + b1
        return centre_x, centre_y

    def TowardDestination(self, destination_x, destination_y):
        """
        About the value of this function returns:
        0: No destination / Movement Completed
        1: Movement not completed(now moving toward the destination)
        """
        RealSpeed = self.speed / RefreshRate # Dynamically adjust the speed depending on the refresh rate
        current_x, current_y = self.GetCentreCoordinate()
        if destination_x == current_x and destination_y == current_y:
            return 0  # Already at the destination
        if destination_x != self.previous_destination_x and destination_y != self.previous_destination_y:
            if current_y != destination_y:
                CalculationVar = (destination_x-current_x) / \
                    (destination_y-current_y)
                distance = math.sqrt(
                    (destination_x-current_x)**2 + (destination_y-current_y)**2)
                self.NumberOfMoves = round(distance / (RealSpeed))
                self.toward_y = RealSpeed / math.sqrt(CalculationVar**2 + 1)
                self.toward_x = abs(CalculationVar * self.toward_y)
                if destination_y - current_y < 0:
                    self.toward_y = -self.toward_y
                if destination_x - current_x < 0:
                    self.toward_x = -self.toward_x

            if current_y == destination_y:  # Prevent DividedByZero Error in CalculationVar
                if destination_x - current_x < 0:
                    self.toward_x = -RealSpeed
                if destination_x - current_x > 0:
                    self.toward_x = RealSpeed
                distance = abs(destination_x - current_x)
                self.NumberOfMoves = round(distance / RealSpeed)
                self.toward_y = 0

            self.previous_destination_x = destination_x
            self.previous_destination_y = destination_y

        if destination_x == -1 or destination_y == -1 or self.NumberOfMoves == 0:  # No destination
            self.status = "IDLE"
            return 0

        if destination_x == self.previous_destination_x and destination_y == self.previous_destination_y:
            if self.NumberOfMoves <= 0:
                self.previous_destination_x = -1  # -1 means no destination
                self.previous_destination_y = -1
                self.status = "IDLE"
                return 0
            if self.NumberOfMoves > 0:
                self.canvas.move(self.tank, self.toward_x, self.toward_y)
                self.canvas.move(self.tank_text, self.toward_x, self.toward_y)
                self.canvas.move(self.direction_label,
                                 self.toward_x, self.toward_y)
                self.direction_point = [
                    self.direction_point[0]+self.toward_x, self.direction_point[1]+self.toward_y]

                self.NumberOfMoves -= 1
                self.status = "MOVING"
                return 1

    def rotate(self, rotation_angle: float):
        """
        Rotation_Times: Positive for counterclockwise, Negative for clockwise
        """
        vertices = self.canvas.coords(self.tank)
        vertices = [vertices[i:i+2] for i in range(0, len(vertices), 2)]
        centre_x, centre_y = self.GetCentreCoordinate()
        """
        x = (m-a)*cosθ - (n-b)*sinθ + a
        y = (m-a)*sinθ + (n-b)*cosθ + b
        """
        angle = math.radians(rotation_angle)
        cos = math.cos(angle)
        sin = math.sin(angle)
        new_vertices = []
        for coordinate in vertices:
            x, y = coordinate[0], coordinate[1]
            x, y = (x-centre_x)*cos - (y-centre_y)*sin + \
                centre_x, (x-centre_x)*sin + (y-centre_y)*cos + centre_y
            new_vertices.append(x)
            new_vertices.append(y)
        direction_x, direction_y = self.direction_point[0], self.direction_point[1]
        direction_x, direction_y = (direction_x-centre_x)*cos - (direction_y-centre_y) * \
            sin + centre_x, (direction_x-centre_x)*sin + \
            (direction_y-centre_y)*cos + centre_y
        self.direction_point = [direction_x, direction_y]

        self.canvas.delete(self.direction_label)
        self.canvas.delete(self.tank)
        self.direction_label = self.canvas.create_line(
            centre_x, centre_y, direction_x, direction_y, arrow=LAST, fill="black")
        self.tank = self.canvas.create_polygon(
            new_vertices, outline=self.team, fill=self.team)

    def GetHit(self, shooter: str, distance: float, part: int):
        """
        Input: The tank name of the shooter, distance from the shooter, part hit by the shooter.
        Output: Whether the tank is destroyed.
        """
        armor = TANK_DATA[self.tank_name][1][part]  # Part: 0 for front, 1 for side, 2 for rear
        DistanceChoices = [0, 100, 300, 500, 1000, 1500, 2000]
        HigherDistances = [0, 100, 300, 500, 1000, 1500, 2000, 3000]
        HigherDistanceChoice = 3000
        for d in DistanceChoices:
            if distance <= d:
                HigherDistanceChoice = d
                break
        HigherDistanceChoiceIndex = HigherDistances.index(HigherDistanceChoice)
        HigherPenetration = TANK_DATA[shooter][0][HigherDistanceChoiceIndex]
        if HigherDistanceChoiceIndex != 0:
            LowerDistanceChoice = DistanceChoices[HigherDistanceChoiceIndex-1]
            LowerPenetration = TANK_DATA[shooter][0][HigherDistanceChoiceIndex-1]
        else:
            LowerDistanceChoice = 0
            LowerPenetration = HigherPenetration - 1
        RealPenetration = (HigherPenetration*(distance-LowerDistanceChoice) + LowerPenetration*(
            HigherDistanceChoice-distance)) / (HigherDistanceChoice-LowerDistanceChoice)
        print(armor, LowerDistanceChoice, distance, HigherDistanceChoice,
              LowerPenetration, HigherPenetration, RealPenetration)
        
        if RealPenetration - armor > -17:
            Destroyed_Probability = 1 / \
                ((500 / ((RealPenetration-armor+17)**2))**2 + 1)
        else:
            Destroyed_Probability = 0
        game.ChangeMessageBoxText(f"Armor: {armor}\nPenetration: {RealPenetration}\nDestruction Rate: {round(Destroyed_Probability,2)}")
        # For further calculation formula details, please see notes.txt
        print(Destroyed_Probability)
        IfDestroyed = random.choices(
            [True, False], [Destroyed_Probability, 1-Destroyed_Probability])
        # game.ChangeMessageBoxText(f"{Destroyed_Probability}, {IfDestroyed}")
        if IfDestroyed == [True]:
            self.status = "DESTROYED"

    def shoot(self, target):
        if target.team == self.team: 
            game.ChangeMessageBoxText("NO Friendly fire!!")
            return
        playsound3.playsound("Cannon-firing.mp3", block=False)
        target_x, target_y = self.GetCentreCoordinate(target=target)
        # Which is the shooter's coordinate(self is the shooter)
        current_x, current_y = self.GetCentreCoordinate(target=self)
        distance = math.sqrt((target_x-current_x)**2 + (target_y-current_y)**2)
        Shell(canvas=game.canvas, shooter=self, target=target)

        ShootArrow = self.canvas.create_line(
            current_x, current_y, target_x, target_y, arrow=LAST, fill='black')
        DistanceLabel = self.canvas.create_text(
            (current_x+target_x)/2+8, (current_y+target_y)/2, text=f"{round(distance)}", fill="black")
        game.tk.after(300, self.canvas.delete, ShootArrow)
        game.tk.after(300, self.canvas.delete, DistanceLabel)

    def run(self):
        if self.IfSelected == False:
            self.canvas.itemconfig(self.tank, fill="#ffffff")
        if self.IfSelected == True:
            self.canvas.itemconfig(self.tank, fill=self.team)
        if self.status == "IDLE":
            pass
        if self.status == "MOVING":
            self.TowardDestination(self.destination_x, self.destination_y)
        if self.status == "DESTROYED":
            playsound3.playsound("Explosion.mp3", block=False)
            self.canvas.delete(self.tank)
            tanks.remove(self)


class Shell:
    def __init__(self, canvas: Canvas, shooter: Tank, target: Tank, speed=10):
        self.canvas = canvas
        self.shooter = shooter
        self.target = target
        self.speed = speed
        self.target_x, self.target_y = self.target.GetCentreCoordinate()
        self.shooter_x, self.shooter_y = self.shooter.GetCentreCoordinate()
        self.shell_id = self.canvas.create_oval(
            self.shooter_x-3, self.shooter_y-3, self.shooter_x+3, self.shooter_y+3, fill="grey")
        self.shell_x = self.shooter_x
        self.shell_y = self.shooter_y
        self.toward_x = 0
        self.toward_y = 0
        self.distance = math.sqrt(
            (self.shooter_x-self.target_x)**2 + (self.shooter_y-self.target_y)**2)
        self.shoot()
        shells.append(self)
        self.previous_coordinate = (self.shell_x, self.shell_y)

    def shoot(self):
        """
        Calculate the route of the shell.
        """
        destination_x, destination_y = self.target_x, self.target_y
        if self.shooter_y != destination_y:
            CalculationVar = (destination_x-self.shooter_x) / \
                (destination_y-self.shooter_y)
            self.toward_y = self.speed / math.sqrt(CalculationVar**2 + 1)
            self.toward_x = abs(CalculationVar * self.toward_y)
            if destination_y - self.shooter_y < 0:
                self.toward_y = -self.toward_y
            if destination_x - self.shooter_x < 0:
                self.toward_x = -self.toward_x

        if self.shooter_y == destination_y:  # Prevent DividedByZero Error in CalculationVar
            if destination_x - self.shooter_x < 0:
                self.toward_x = -self.speed
            if destination_x - self.shooter_y > 0:
                self.toward_x = self.speed
            self.toward_y = 0

    def travel(self):
        """
        The shell travels towards the target, and determine which side of the target tank it hits.
        """
        target_vertices = self.canvas.coords(self.target.tank)
        IndexList = [[0, 1, 2, 3], [2, 3, 4, 5], [4, 5, 6, 7], [6, 7, 0, 1]]
        toward_x, toward_y = self.toward_x, self.toward_y
        self.shell_x += toward_x
        self.shell_y += toward_y
        self.canvas.move(self.shell_id, toward_x, toward_y)
        for side in IndexList:

            if self.shell_x <= 0 or self.shell_x >= 1512 or self.shell_y <= 0 or self.shell_y >= 982 or self.target.status == "DESTROYED":
                print("NOT HIT")
                game.ChangeDebugMessage("NOT HIT")
                shells.remove(self)
                del (self)
                return -1   # Not Hit
            index = IndexList.index(side)
            x1, y1, x2, y2 = target_vertices[side[0]], target_vertices[side[1]
                                                                       ], target_vertices[side[2]], target_vertices[side[3]]
            C = (x1, y1)
            D = (x2, y2)
            A = self.previous_coordinate
            B = (self.shell_x, self.shell_y)
            if is_intersect(A, B, C, D) == True:
                if index == 3:
                    game.ChangeDebugMessage("HIT REAR")
                    self.target.GetHit(
                        shooter=self.shooter.tank_name, part=2, distance=self.distance)
                    shells.remove(self)
                    self.canvas.delete(self.shell_id)
                    del (self)
                    return 2
                if index == 2:
                    game.ChangeDebugMessage("HIT SIDE")
                    # 0 for front, 1 for side, 2 for rear
                    self.target.GetHit(
                        shooter=self.shooter.tank_name, part=1, distance=self.distance)
                    shells.remove(self)
                    self.canvas.delete(self.shell_id)
                    del (self)
                    return 1
                if index == 1:
                    game.ChangeDebugMessage("HIT FRONT")
                    self.target.GetHit(
                        shooter=self.shooter.tank_name, part=0, distance=self.distance)
                    shells.remove(self)
                    self.canvas.delete(self.shell_id)
                    del (self)
                    return 0
                if index == 0:
                    game.ChangeDebugMessage("HIT SIDE")
                    # 0 for front, 1 for side, 2 for rear
                    self.target.GetHit(
                        shooter=self.shooter.tank_name, part=1, distance=self.distance)
                    shells.remove(self)
                    self.canvas.delete(self.shell_id)
                    del (self)
                    return 1
                
        for bunker in bunkers: # Hit the bunker
            if if_point_in_polygon((self.shell_x,self.shell_y), bunker.bunker):
                shells.remove(self)
                self.canvas.delete(self.shell_id)
                del(self)
                return "HIT the bunker"
        self.previous_coordinate = (self.shell_x, self.shell_y)

class Bunker:
    def __init__(self, canvas:Canvas, vertices:list):
        global bunkers
        bunkers.append(self)
        self.canvas = canvas
        self.vertices = vertices
        self.bunker = self.canvas.create_polygon(vertices, fill="grey")


game = Game()
tank1 = Tank(canvas=game.canvas, tank_name="PzIV H", spawn_point=[50, 50], team="RED")
tank2 = Tank(canvas=game.canvas, tank_name="PzIII J", spawn_point=[50, 80], team="RED")
tank3 = Tank(canvas=game.canvas, tank_name="T34", spawn_point=[50, 550], team="RED")
tank4 = Tank(canvas=game.canvas, tank_name="PzIII J", spawn_point=[50, 600], team="RED")
tank5 = Tank(canvas=game.canvas, tank_name="PzIV H", spawn_point=[1300, 100], team="BLUE")
tank6 = Tank(canvas=game.canvas, tank_name="PzIII J", spawn_point=[1300, 150], team="BLUE")
tank7 = Tank(canvas=game.canvas, tank_name="PzIII J", spawn_point=[1300, 600], team="BLUE")
tank8 = Tank(canvas=game.canvas, tank_name="T34", spawn_point=[1300, 700], team="BLUE")

bunker1 = Bunker(canvas=game.canvas, vertices=[400,400,300,300,300,400,400,450])
bunker2 = Bunker(canvas=game.canvas, vertices=[600,400,800,100,700,450,750,450])
bunker3 = Bunker(canvas=game.canvas, vertices=[800,900,600,500,700,400,800,450])


print(game.canvas_width, game.canvas_height)

tick_time = 0

while True:
    if GAMING == True:
        T1 = time.time()
        Tick = True
        game.run()
        game.tk.update()
        Tick = False
        T2 = time.time()
        TickDynamicAdjustment(T2-T1)
    if GAMING == False:
        break

sys.exit()

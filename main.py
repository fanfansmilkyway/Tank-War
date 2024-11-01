from tkinter import *
import math
import random
import time
import sys

GAMING = True

# "Tank Name": [Attack(0m, 100m, 300m, 500m, 1000m, 1500m, 2000m, 3000m)mm, Relative Armor(front, side, rear), Speed(pixel / 0.5s)]
TANK_DATA = {"T34": [[100, 85, 80, 73, 68, 62, 57, 45], [520, 520, 460], 4.86],
             "PzIII J": [[60, 55, 50, 57, 47, 28, 21, 15, 5], [500, 300, 450], 4.16],
             "PzIV H": [[140, 135, 130, 123, 109, 97, 86, 68], [800, 300, 200], 2.78]}

tanks = []  # The list which stores all the tanks

BenchMarkTime = time.time()


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
        Rotate the tank counterclockwise for 15 degrees.
        """
        for tank in self.selected_tanks:
            tank.rotate(-1)

    def RotateClockwise(self, event):
        """
        Rotate the tank clockwise for 15 degrees.
        """
        for tank in self.selected_tanks:
            tank.rotate(1)

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
    def __init__(self, canvas: Canvas, tank_name: str, spawn_point: list = [100, 100]):
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
        self.vertices = [self.spawn_point[0]-8, self.spawn_point[1]-6, self.spawn_point[0]+8, self.spawn_point[1] -
                         6, self.spawn_point[0]+8, self.spawn_point[1]+6, self.spawn_point[0]-8, self.spawn_point[1]+6]
        self.tank = self.canvas.create_polygon(
            self.vertices, outline="red", fill='white')
        self.tank_text = self.canvas.create_text(
            self.spawn_point[0], self.spawn_point[1]-14, fill="black", text=self.tank_name, font=("Courier", "10"))
        self.direction_label = self.canvas.create_line(
            self.spawn_point[0], self.spawn_point[1], self.spawn_point[0]+20, self.spawn_point[1], arrow=LAST, fill="black")
        self.direction_point = [self.spawn_point[0]+20, self.spawn_point[1]]
        print(self.canvas.coords(self.tank))
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
        current_x, current_y = self.GetCentreCoordinate()
        if destination_x == current_x and destination_y == current_y:
            return 0  # Already at the destination
        if destination_x != self.previous_destination_x and destination_y != self.previous_destination_y:
            if current_y != destination_y:
                CalculationVar = (destination_x-current_x) / \
                    (destination_y-current_y)
                distance = math.sqrt(
                    (destination_x-current_x)**2 + (destination_y-current_y)**2)
                self.NumberOfMoves = round(distance / self.speed)
                self.toward_y = self.speed / math.sqrt(CalculationVar**2 + 1)
                self.toward_x = abs(CalculationVar * self.toward_y)
                if destination_y - current_y < 0:
                    self.toward_y = -self.toward_y
                if destination_x - current_x < 0:
                    self.toward_x = -self.toward_x

            if current_y == destination_y:  # Prevent DividedByZero Error in CalculationVar
                if destination_x - current_x < 0:
                    self.toward_x = -self.speed
                if destination_x - current_x > 0:
                    self.toward_x = self.speed
                distance = abs(destination_x - current_x)
                self.NumberOfMoves = round(distance / self.speed)
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
                self.canvas.update()

                self.NumberOfMoves -= 1
                self.status = "MOVING"
                return 1

    def rotate(self, rotation_times: int):
        """
        Rotation_Times: times of rotating 15 degrees. Positive for counterclockwise, Negative for clockwise
        """
        vertices = self.canvas.coords(self.tank)
        vertices = [vertices[i:i+2] for i in range(0, len(vertices), 2)]
        centre_x, centre_y = self.GetCentreCoordinate()
        """
        x = (m-a)*cosθ - (n-b)*sinθ + a
        y = (m-a)*sinθ + (n-b)*cosθ + b
        """
        angle = math.radians(rotation_times*15)
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
            new_vertices, outline="red", fill='white')

    def GetHit(self, shooter: str, distance, part: int):
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
        # For further calculation formula details, please see notes.txt
        print(Destroyed_Probability)
        IfDestroyed = random.choices(
            [True, False], [Destroyed_Probability, 1-Destroyed_Probability])
        # game.ChangeMessageBoxText(f"{Destroyed_Probability}, {IfDestroyed}")
        if IfDestroyed == [True]:
            self.status = "DESTROYED"

    def shell(self, target, speed=0.1):
        target_vertices = self.canvas.coords(target.tank)
        target_x, target_y = target.GetCentreCoordinate()
        current_x, current_y = self.GetCentreCoordinate(target=self)

        IndexList = [[0, 1, 2, 3], [2, 3, 4, 5], [4, 5, 6, 7], [6, 7, 0, 1]]
        TargetTankSides = []  # Linear functions list [[k1,b1],[k2,b2],[k3,b3],[k4,b4]]

        self.canvas.create_line(target_vertices[0], target_vertices[1],
                                target_vertices[2], target_vertices[3], arrow=LAST, fill="red")
        # Shell travelling
        shell_x = current_x
        shell_y = current_y

        destination_x, destination_y = target_x, target_y
        if current_y != destination_y:
            CalculationVar = (destination_x-current_x) / \
                (destination_y-current_y)
            toward_y = speed / math.sqrt(CalculationVar**2 + 1)
            toward_x = abs(CalculationVar * toward_y)
            if destination_y - current_y < 0:
                toward_y = -toward_y
            if destination_x - current_x < 0:
                toward_x = -toward_x

        if current_y == destination_y:  # Prevent DividedByZero Error in CalculationVar
            if destination_x - current_x < 0:
                toward_x = -speed
            if destination_x - current_x > 0:
                toward_x = speed
            toward_y = 0

        while True:
            shell_x += toward_x
            shell_y += toward_y
            for side in IndexList:
                index = IndexList.index(side)
                x1, y1, x2, y2 = target_vertices[side[0]], target_vertices[side[1]], target_vertices[side[2]], target_vertices[side[3]]
                # Determine whether the shell is 
                if abs(math.sqrt((x1-x2)**2 + (y1-y2)**2) - math.sqrt((x1-shell_x)**2 + (y1-shell_y)**2) - math.sqrt((x2-shell_x)**2 + (y2-shell_y)**2)) <= 1:
                    if index == 3:
                        game.ChangeDebugMessage("HIT REAR")
                        return 2
                    if index == 2:
                        game.ChangeDebugMessage("HIT SIDE")
                        # 0 for front, 1 for side, 2 for rear
                        return 1
                    if index == 1:
                        game.ChangeDebugMessage("HIT FRONT")
                        return 0
                    if index == 0:
                        game.ChangeDebugMessage("HIT SIDE")
                        # 0 for front, 1 for side, 2 for rear
                        return 1

            print(f"CYCLE{shell_x, shell_y}")
            if shell_x <= 0 or shell_x >= 1512 or shell_y <= 0 or shell_y >= 982:
                print("NOT HIT")
                game.ChangeDebugMessage("NOT HIT")
                return -1   # Not Hit

    def shoot(self, target):
        target_x, target_y = self.GetCentreCoordinate(target=target)
        # Which is the shooter's coordinate(self is the shooter)
        current_x, current_y = self.GetCentreCoordinate(target=self)
        hit_part = -1  # 0 for front, 1 for side, 2 for rear
        distance = math.sqrt((target_x-current_x)**2 + (target_y-current_y)**2)
        hit_part = self.shell(target=target)

        target.GetHit(shooter=self.tank_name, distance=distance, part=hit_part)

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
            self.canvas.itemconfig(self.tank, fill="#ff0000")
        if self.status == "IDLE":
            pass
        if self.status == "MOVING" and IfTriggered == True:
            self.TowardDestination(self.destination_x, self.destination_y)
        if self.status == "DESTROYED":
            self.canvas.delete(self.tank)
            tanks.remove(self)


game = Game()
tank1 = Tank(canvas=game.canvas, tank_name="PzIV H", spawn_point=[50, 50])
tank2 = Tank(canvas=game.canvas, tank_name="PzIII J", spawn_point=[100, 800])
tank3 = Tank(canvas=game.canvas, tank_name="T34", spawn_point=[1300, 800])

print(game.canvas_width, game.canvas_height)
IfTriggered = False  # Triggered by function "FrequencyGenerator"

while True:
    if GAMING == True:
        FrequencyGenerator(frequency=0.5)
        game.run()
        game.tk.update_idletasks()
        game.tk.update()
        time.sleep(0.01)  # 100 fps
    if GAMING == False:
        break

sys.exit()

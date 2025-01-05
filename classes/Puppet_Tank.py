from tkinter import *
import random
import math
from Tank_Data import TANK_CAPABILITY # Import the basic data of the tanks.
from global_functions import *
from classes.Shell import Shell
import playsound3

class Puppet_Tank:
    def __init__(self, id, game, canvas: Canvas, tank_name: str, team:str, spawn_point: list = [100, 100]):
        print("CREATE PUPPET TANK")
        self.game = game
        self.game.tank_id[id] = self
        self.tank_name = tank_name
        self.team = team  # team name represents its color
        self.id = id
        #self.team = team
        try:
            self.capability = TANK_CAPABILITY[self.tank_name]
        except KeyError:
            print(f"[ERROR] Unknown tank type: {self.tank_name}")
            exit()
        self.speed = self.capability[2] # pix/sec
        self.reloading_speed = self.capability[3]
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
        self.reloading_indicator = self.canvas.create_text(
            self.spawn_point[0], self.spawn_point[1]-20, fill="green", text="*", font=("Courier", "18"))
        self.direction_point = [self.spawn_point[0]+20, self.spawn_point[1]]

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
        self.IfReloaded = True

        self.game.tanks.append(self)
        

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
        RealSpeed = self.speed / self.game.RefreshRate # Dynamically adjust the speed depending on the refresh rate
        current_x, current_y = self.GetCentreCoordinate()
        if abs(destination_x-current_x)<0.5 and abs(destination_y-current_y)<0.5:
            self.status = "IDLE"
            return 0  # Already at the destination
        
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

        # Determine whether the next step will touch the bunker. If it will, then stop the moving process
        for bunker in self.game.bunkers:
            if if_point_in_polygon((current_x+self.toward_x, current_y+self.toward_y), bunker.vertices):
                self.status = "IDLE"
                self.NumberOfMoves = -1
                return 0
            
        self.canvas.move(self.tank, self.toward_x, self.toward_y)
        self.canvas.move(self.tank_text, self.toward_x, self.toward_y)
        self.canvas.move(self.direction_label,
                                 self.toward_x, self.toward_y)
        self.canvas.move(self.reloading_indicator,
                                 self.toward_x, self.toward_y)
        self.direction_point = [
                    self.direction_point[0]+self.toward_x, self.direction_point[1]+self.toward_y]

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
        armor = TANK_CAPABILITY[self.tank_name][1][part]  # Part: 0 for front, 1 for side, 2 for rear
        # Calculate the real penetration
        DistanceChoices = [0, 100, 300, 500, 1000, 1500, 2000]
        HigherDistances = [0, 100, 300, 500, 1000, 1500, 2000, 3000]
        HigherDistanceChoice = 3000
        for d in DistanceChoices:
            if distance <= d:
                HigherDistanceChoice = d
                break
        HigherDistanceChoiceIndex = HigherDistances.index(HigherDistanceChoice)
        HigherPenetration = TANK_CAPABILITY[shooter][0][HigherDistanceChoiceIndex]
        if HigherDistanceChoiceIndex != 0:
            LowerDistanceChoice = DistanceChoices[HigherDistanceChoiceIndex-1]
            LowerPenetration = TANK_CAPABILITY[shooter][0][HigherDistanceChoiceIndex-1]
        else:
            LowerDistanceChoice = 0
            LowerPenetration = HigherPenetration - 1
        RealPenetration = (HigherPenetration*(distance-LowerDistanceChoice) + LowerPenetration*(HigherDistanceChoice-distance)) / (HigherDistanceChoice-LowerDistanceChoice)
        # Calculate the detroyed rate
        if RealPenetration - armor > -17:
            # For further calculation formula details, please see notes.txt
            Destroyed_Probability = 1 / ((500 / ((RealPenetration-armor+17)**2))**2 + 1)
        else:
            Destroyed_Probability = 0
        self.game.ChangeMessageBoxText(f"Armor: {armor}\nPenetration: {RealPenetration}\nDestruction Rate: {round(Destroyed_Probability,2)}")
        print(Destroyed_Probability)
        
        IfDestroyed = random.choices(
            [True, False], [Destroyed_Probability, 1-Destroyed_Probability])
        if IfDestroyed == [True]:
            self.status = "DESTROYED"

    def shoot(self, target):
        if target.team == self.team: 
            self.game.ChangeMessageBoxText("NO Friendly fire!!")
            return
        if self.IfReloaded == False:
            playsound3.playsound("./mp3/Reloading_hasn't_completed_yet.mp3", block=False)
            return
        
        playsound3.playsound("./mp3/Cannon-firing.mp3", block=False)
        self.IfReloaded = False
        self.canvas.itemconfig(self.reloading_indicator, fill="red")

        target_x, target_y = self.GetCentreCoordinate(target=target)
        current_x, current_y = self.GetCentreCoordinate(target=self)
        distance = math.sqrt((target_x-current_x)**2 + (target_y-current_y)**2)
        Shell(game=self.game, canvas=self.game.canvas, shooter=self, target=target) # Create the shell

        ShootArrow = self.canvas.create_line(
            current_x, current_y, target_x, target_y, arrow=LAST, fill='black')
        DistanceLabel = self.canvas.create_text(
            (current_x+target_x)/2+8, (current_y+target_y)/2, text=f"{round(distance)}", fill="black")
        
        self.game.tk.after(300, self.canvas.delete, ShootArrow)
        self.game.tk.after(300, self.canvas.delete, DistanceLabel)
        self.game.tk.after(round(self.reloading_speed*1000), self.reload)
    
    def reload(self):
        self.IfReloaded = True
        playsound3.playsound("./mp3/Reload_Completed.mp3", block=False)
        self.canvas.itemconfig(self.reloading_indicator, fill="green")

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
            playsound3.playsound("./mp3/Explosion.mp3", block=False)
            self.canvas.delete(self.tank)
            self.game.tanks.remove(self)
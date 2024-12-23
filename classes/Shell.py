from tkinter import *
import math

import global_variables as g_val
from global_functions import *

class Shell:
    def __init__(self, game, canvas: Canvas, shooter, target, speed=1000):
        self.game = game
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
        self.TowardTarget()
        g_val.shells.append(self)
        self.previous_coordinate = (self.shell_x, self.shell_y)

    def TowardTarget(self):
        """
        Calculate the route of the shell.
        """
        RealSpeed = self.speed / g_val.RefreshRate
        destination_x, destination_y = self.target_x, self.target_y
        if self.shooter_y != destination_y:
            CalculationVar = (destination_x-self.shooter_x) / \
                (destination_y-self.shooter_y)
            self.toward_y = RealSpeed / math.sqrt(CalculationVar**2 + 1)
            self.toward_x = abs(CalculationVar * self.toward_y)
            if destination_y - self.shooter_y < 0:
                self.toward_y = -self.toward_y
            if destination_x - self.shooter_x < 0:
                self.toward_x = -self.toward_x

        if self.shooter_y == destination_y:  # Prevent DividedByZero Error in CalculationVar
            if destination_x - self.shooter_x < 0:
                self.toward_x = -RealSpeed
            if destination_x - self.shooter_y > 0:
                self.toward_x = RealSpeed
            self.toward_y = 0

    def travel(self):
        """
        The shell travels towards the target, and determine which side of the target tank it hits.
        Side hit: 0 for front, 1 for side, 2 for rear
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
                self.game.ChangeDebugMessage("NOT HIT")
                g_val.shells.remove(self)
                return -1   # Not Hit
            index = IndexList.index(side)
            x1, y1, x2, y2 = target_vertices[side[0]], target_vertices[side[1]
                                                                       ], target_vertices[side[2]], target_vertices[side[3]]
            C = (x1, y1)
            D = (x2, y2)
            A = self.previous_coordinate
            B = (self.shell_x, self.shell_y)
            if if_intersect(A, B, C, D) == True:
                # 0 for front, 1 for side, 2 for rear
                if index == 3:
                    self.game.ChangeDebugMessage("HIT REAR")
                    self.target.GetHit(
                        shooter=self.shooter.tank_name, part=2, distance=self.distance)
                    g_val.shells.remove(self)
                    self.canvas.delete(self.shell_id)
                    return 2
                if index == 2:
                    self.game.ChangeDebugMessage("HIT SIDE")
                    self.target.GetHit(
                        shooter=self.shooter.tank_name, part=1, distance=self.distance)
                    g_val.shells.remove(self)
                    self.canvas.delete(self.shell_id)
                    return 1
                if index == 1:
                    self.game.ChangeDebugMessage("HIT FRONT")
                    self.target.GetHit(
                        shooter=self.shooter.tank_name, part=0, distance=self.distance)
                    g_val.shells.remove(self)
                    self.canvas.delete(self.shell_id)
                    return 0
                if index == 0:
                    self.game.ChangeDebugMessage("HIT SIDE")
                    self.target.GetHit(
                        shooter=self.shooter.tank_name, part=1, distance=self.distance)
                    g_val.shells.remove(self)
                    self.canvas.delete(self.shell_id)
                    return 1
                
        for bunker in g_val.bunkers: # Hit the bunker
            if if_point_in_polygon((self.shell_x,self.shell_y), bunker.vertices):
                g_val.shells.remove(self)
                self.canvas.delete(self.shell_id)
                del(self)
                return "HIT the bunker"
            
        self.previous_coordinate = (self.shell_x, self.shell_y)
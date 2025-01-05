# The obtacles
from tkinter import *

class Bunker:
    def __init__(self, game, canvas:Canvas, vertices:list):
        self.game = game
        self.game.bunkers.append(self)
        self.canvas = canvas
        self.vertices = vertices
        self.bunker = self.canvas.create_polygon(vertices, fill="grey")
from tkinter import *
import global_variables as g_val
from global_functions import *

class Bunker:
    def __init__(self, canvas:Canvas, vertices:list):
        g_val.bunkers.append(self)
        self.canvas = canvas
        self.vertices = vertices
        self.bunker = self.canvas.create_polygon(vertices, fill="grey")
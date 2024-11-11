from engine import Animation
import pygame
from pygame.locals import *
from .constants import *
from .gui import FONT


def lerp(x, y, delta):
    return [(x_val * (1.0 - delta)) + (y_val * delta) for x_val, y_val in zip(x, y)]


class ChangeColor(Animation):
    def __init__(self, row, col, start_color, end_color, duration):
        super().__init__()
        self.row = row
        self.col = col
        self.start_color = start_color
        self.end_color = end_color
        self.duration = duration
        self.elapsed = 0

    def update(self, engine, delta_time):
        self.elapsed += delta_time / self.duration
        color = lerp(self.start_color, self.end_color, self.elapsed)
        if self.elapsed >= 1:
            self.done()
        else:
            engine.gui_manager.set_cell_color(self.row, self.col, color)

    def draw(self, engine, surface):
        pass

import pygame as pg

from .base import Entity
from scripts.volume import Light

hit_box_size = (110, 110)

class Portal(Entity):
    def __init__(self, spawn_position : pg.Vector2):
        rect = pg.Rect(spawn_position, hit_box_size)
        super().__init__("portal", rect)

        self.light = Light(500, pg.Vector2(self.rect.center), 50)
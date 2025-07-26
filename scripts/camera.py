import pygame as pg
import random

from .objects import *
from scripts.constants import *

SHAKE_DECREASE = 200
WHOLE_SCREEN_RECT = pg.Rect((0, 0), SCREEN_SIZE)

class Camera2D(GameObject):
    def __init__(self, scale : float, position : pg.Vector2, anchor : pg.Vector2 = pg.Vector2(0.5, 0.5)):
        super().__init__()
        self._scale = round(scale * 2) / 2
        self.position = position
        self.anchor = anchor
        
        self.shake_amount = 0.0
        self.shake_offset = pg.Vector2(0, 0)

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        self._scale = max(round(value * 2) / 2, 0.5)
    
    @property
    def anchor_pixel(self):
        return pg.Vector2(
            SCREEN_SIZE.x * self.anchor.x,
            SCREEN_SIZE.y * self.anchor.y
        )

    def world_to_screen(self, world_pos: pg.Vector2) -> pg.Vector2:
        return self.anchor_pixel + (world_pos - (self.position + self.shake_offset)) * self.scale

    def screen_to_world(self, screen_pos: pg.Vector2) -> pg.Vector2:
        return (screen_pos - self.anchor_pixel) / self.scale + (self.position + self.shake_offset)
    
    def get_scaled_surface(self, surface : pg.Surface) -> pg.Surface:
        return surface if self.scale == 1 else pg.transform.scale_by(surface, self.scale)
    
    def world_rect_to_screen_rect(self, world_rect: pg.Rect) -> pg.Rect:
        screen_pos = self.world_to_screen(pg.Vector2(world_rect.topleft))
        screen_size = pg.Vector2(world_rect.size) * self.scale
        return pg.Rect(screen_pos, screen_size)

    def is_in_view(self, world_rect : pg.Rect):
        return WHOLE_SCREEN_RECT.colliderect(self.world_rect_to_screen_rect(world_rect))

    def shake(self, amount : float):
        self.shake_amount = max(self.shake_amount, amount)

    def on_update(self):
        if self.shake_amount > 0:
            self.shake_offset.x = random.uniform(-self.shake_amount, self.shake_amount)
            self.shake_offset.y = random.uniform(-self.shake_amount, self.shake_amount)
            
            self.shake_amount -= SHAKE_DECREASE * self.app.dt
            if self.shake_amount < 0:
                self.shake_amount = 0.0
                self.shake_offset = pg.Vector2(0, 0)
        else:
            self.shake_amount = 0
            self.shake_offset = pg.Vector2(0, 0)
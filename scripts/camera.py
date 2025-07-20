import pygame as pg
from datas.const import *

class Camera2D:
    def __init__(self, offset : pg.Vector2, scale : float = 1, anchor : pg.Vector2 = pg.Vector2(0.5, 0.5)):
        self.scale = scale
        self.offset = offset
        self.anchor = anchor

    def world_to_screen(self, world_pos: pg.Vector2) -> pg.Vector2:
        anchor_pixel = pg.Vector2(
            SCREEN_SIZE.x * self.anchor.x,
            SCREEN_SIZE.y * self.anchor.y
        )
        return anchor_pixel + (world_pos - self.offset) * self.scale

    def screen_to_world(self, screen_pos: pg.Vector2) -> pg.Vector2:
        anchor_pixel = pg.Vector2(
            SCREEN_SIZE.x * self.anchor.x,
            SCREEN_SIZE.y * self.anchor.y
        )
        return (screen_pos - anchor_pixel) / self.scale + self.offset
    
    def get_scaled_surface(self, surface : pg.Surface) -> pg.Surface:
        return pg.transform.scale_by(surface, self.scale)

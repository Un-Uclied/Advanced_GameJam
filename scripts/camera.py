#외부 라이브러리 임포트
import pygame as pg
from datas.const import *

class Camera2D:
    screen_size = pg.Vector2(SCREEN_SIZE)
    def __init__(self, scale : float, offset : pg.Vector2, anchor : pg.Vector2 = pg.Vector2(0.5, 0.5)):
        self.scale = scale
        self.offset = offset
        self.anchor = anchor

    def world_to_screen(self, world_pos: pg.Vector2) -> pg.Vector2:
        anchor_pixel = pg.Vector2(
            self.screen_size.x * self.anchor.x,
            self.screen_size.y * self.anchor.y
        )
        return anchor_pixel + (world_pos - self.offset) * self.scale

    def screen_to_world(self, screen_pos: pg.Vector2) -> pg.Vector2:
        anchor_pixel = pg.Vector2(
            self.screen_size.x * self.anchor.x,
            self.screen_size.y * self.anchor.y
        )
        return (screen_pos - anchor_pixel) / self.scale + self.offset
    
    def get_scaled_surface(self, surface : pg.Surface, original_size : pg.Vector2 | None) -> pg.Surface:
        original_size = surface.get_size()
        transform_size = (original_size[0] * self.scale, original_size[1] * self.scale)
        return pg.transform.scale(surface, transform_size)
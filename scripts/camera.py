import pygame as pg
from datas.const import *

class Camera2D:
    def __init__(self, scale : float, offset : pg.Vector2, anchor : pg.Vector2 = pg.Vector2(0.5, 0.5)):
        self._scale = round(scale * 2) / 2
        self.offset = offset
        self.anchor = anchor

    #Im a trash coder bro.. 그냥 scale은 1로 나두는게 젤 좋을듯 최적화 하기 귀찮기도 한데 scale이 1이면 연산 안해서 성능에 더 좋음
    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        self._scale = max(round(value * 2) / 2, 0.5)
        
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
        if self.scale == 1: return surface
        return pg.transform.scale_by(surface, self.scale)

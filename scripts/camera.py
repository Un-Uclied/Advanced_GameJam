import pygame as pg
import random

from .objects import *
from datas.const import *

SHAKE_DECREASE = 200 # 쉐이크 감소율

class Camera2D(GameObject):
    def __init__(self, scale : float, offset : pg.Vector2, anchor : pg.Vector2 = pg.Vector2(0.5, 0.5)):
        super().__init__()
        self._scale = round(scale * 2) / 2
        self.offset = offset
        self.anchor = anchor

        self.shake_amount = 0.0
        self.shake_offset = pg.Vector2(0, 0)

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

        return anchor_pixel + (world_pos - (self.offset + self.shake_offset)) * self.scale

    def screen_to_world(self, screen_pos: pg.Vector2) -> pg.Vector2:
        anchor_pixel = pg.Vector2(
            SCREEN_SIZE.x * self.anchor.x,
            SCREEN_SIZE.y * self.anchor.y
        )

        return (screen_pos - anchor_pixel) / self.scale + (self.offset + self.shake_offset)
    
    def get_scaled_surface(self, surface : pg.Surface) -> pg.Surface:
        if self.scale == 1: return surface
        return pg.transform.scale_by(surface, self.scale)

    def shake(self, amount: float):
        #한번 부르면 타격 효과나 그런 느낌? 몇초 동안 부르면 보스가 포효하는 그런 느낌 ㅋ
        self.shake_amount = max(self.shake_amount, amount) # 기존 쉐이크보다 강하면 바꿈

    def on_update(self):
        if self.shake_amount > 0:
            self.shake_offset.x = random.uniform(-self.shake_amount, self.shake_amount)
            self.shake_offset.y = random.uniform(-self.shake_amount, self.shake_amount)
            
            self.shake_amount -= SHAKE_DECREASE * self.app.dt
            if self.shake_amount < 0:
                self.shake_amount = 0.0
                self.shake_offset = pg.Vector2(0, 0) # 쉐이크 끝나면 오프셋 초기화
        else:
            self.shake_amount = 0
            self.shake_offset = pg.Vector2(0, 0) # 쉐이크가 없으면 오프셋 초기화
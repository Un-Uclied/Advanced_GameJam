import pygame as pg
import random

from scripts.objects import *
from scripts.constants import *

SHAKE_DECREASE = 200

class Camera2D(GameObject):
    def __init__(self, scale, position, anchor=pg.Vector2(0.5, 0.5)):
        super().__init__()
        self._scale = scale
        self.position = position
        self.anchor = anchor

        self.shake_offset = pg.Vector2()
        self.shake_amount = 0.0

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        '''scale은 타일맵 버그를 방지하기 위해 .5, 1, 2.5 ... 이런식으로만 설정 가능'''
        self._scale = max(round(value * 2) / 2, 0.5)

    def update(self):
        super().update()
        if self.shake_amount > 0:
            self.shake_offset = pg.Vector2(
                random.uniform(-self.shake_amount, self.shake_amount),
                random.uniform(-self.shake_amount, self.shake_amount)
            )
            self.shake_amount -= SHAKE_DECREASE * self.app.dt
            if self.shake_amount < 0:
                self.shake_amount = 0.0
                self.shake_offset = pg.Vector2()
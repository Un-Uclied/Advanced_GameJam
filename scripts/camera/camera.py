import pygame as pg
import random

from scripts.core import *
from scripts.constants import *

SHAKE_DECREASE = 200

class Camera2D(GameObject):
    def __init__(self, position, anchor=pg.Vector2(0.5, 0.5)):
        super().__init__()
        self.position = position
        self.anchor = anchor

        self.shake_offset = pg.Vector2()
        self.shake_amount = 0.0

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
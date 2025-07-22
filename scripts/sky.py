import pygame as pg

from datas.const import *
from .objects import *

class Sky(GameObject):
    def __init__(self, asset_key : str = "sky"):
        super().__init__()
        self.asset_key = asset_key

    def on_draw(self):
        super().on_draw()
        self.app.surfaces[LAYER_BG].blit(self.app.ASSET_BACKGROUND[self.asset_key], (0, 0))
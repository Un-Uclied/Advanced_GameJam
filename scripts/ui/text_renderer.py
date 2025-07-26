import pygame as pg

from scripts.constants import *
from scripts.objects import GameObject

BASE_FONT_PATH = "assets/fonts/"

class TextRenderer(GameObject):
    def __init__(self, 
                 start_text : str,
                 pos: pg.Vector2,
                 font_name : str = "default",
                 font_size: int = 24,
                 color: pg.Color = pg.Color(255, 255, 255)):
        
        super().__init__()
        self.text = start_text
        self.pos = pos
        self.color = color
        self.font = pg.font.Font(BASE_FONT_PATH + self.app.ASSETS["fonts"][font_name], font_size)

    def on_draw(self):
        text_surf = self.font.render(self.text, False, self.color)

        screen = self.app.surfaces[LAYER_INTERFACE]
        screen.blit(text_surf, self.pos)
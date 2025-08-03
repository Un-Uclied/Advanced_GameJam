import pygame as pg

from scripts.constants import *
from scripts.backgrounds import *
from scripts.ui import *
from .base import Scene

class InfoScene(Scene):
    def on_scene_start(self):
        TextRenderer("[ESC]", pg.Vector2(10, 10), font_name="bold", font_size=20, anchor=pg.Vector2(0, 0))

        super().on_scene_start()
        
        Sky()

    def update(self):
        super().update()
        for event in self.app.events:
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.app.change_scene("main_menu_scene")
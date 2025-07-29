import pygame as pg

from scripts.constants import *
from scripts.volume import Sky
from scripts.ui import *

from .base.scene import Scene
class SettingsScene(Scene):
    def on_scene_start(self):
        super().on_scene_start()
        Sky()

    def update(self):
        super().update()
        for event in self.app.events:
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.app.change_scene("main_menu_scene")
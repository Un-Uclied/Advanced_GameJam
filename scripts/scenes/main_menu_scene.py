import pygame as pg

from .base.scene import Scene

from scripts.volume import Sky
from scripts.ui import ImageButton

class MainMenuScene(Scene):
    def on_scene_start(self):
        super().on_scene_start()
        Sky()

        def callback(name, button):
            if name == "temp":
                self.app.change_scene("main_game_scene")

        ImageButton("temp", pg.Vector2(400, 400), callback)
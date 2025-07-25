import pygame as pg

from scripts.constants import *
from scripts.camera import Camera2D
from scripts.ui import TextRenderer
from scripts.objects import GameObject

class Scene:
    def __init__(self):
        from scripts.core.app import App
        self.app = App.singleton
    
    def on_scene_start(self):
        self.camera = Camera2D(scale=1, position=pg.Vector2(0, 0))

        self.fps_text_renderer = TextRenderer("??", pg.Vector2(SCREEN_SIZE.x - 55, 10), color="green")

    def on_scene_end(self):
        GameObject.all_objects.clear()

    def update_fps_text(self):
        self.fps_text_renderer.text = str(round(self.app.clock.get_fps()))
    
    def on_update(self):
        self.update_fps_text()
        GameObject.update_all()

    def on_draw(self):
        GameObject.draw_all()
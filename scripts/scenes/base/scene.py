import pygame as pg

from scripts.constants import *
from scripts.camera import *
from scripts.ui import *
from scripts.core import *
from scripts.vfx import *

class Scene:
    def __init__(self):
        from scripts.app import App
        self.app = App.singleton
    
    def on_scene_start(self):
        self.camera = Camera2D(position=pg.Vector2(0, 0))
        self.fps_text_renderer = TextRenderer("??", pg.Vector2(SCREEN_SIZE.x - 55, 10), color="green")
        self.event_bus = EventBus()
        
    def on_scene_end(self):
        GameObject.all_objects.clear()
    
    def update(self):
        '''GameObject.update_all()이 불리는 메소드'''

        self.fps_text_renderer.text = str(round(self.app.clock.get_fps()))
        
        GameObject.update_all()

    def draw(self):
        '''GameObject.update_all()이 불리는 메소드 (paused여도 다 그림.)'''
        GameObject.draw_all()
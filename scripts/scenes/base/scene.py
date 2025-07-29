import pygame as pg

from scripts.constants import *
from scripts.camera import Camera2D
from scripts.ui import TextRenderer
from scripts.entities.base import Entity
from scripts.objects import GameObject
from scripts.vfx import *

class Scene:
    def __init__(self):
        from scripts.app import App
        self.app = App.singleton

        self.fading = False
    
    def on_scene_start(self):
        self.camera = Camera2D(scale=1, position=pg.Vector2(0, 0))
        self.fps_text_renderer = TextRenderer("??", pg.Vector2(SCREEN_SIZE.x - 55, 10), color="green")

        self.fading = True

        ScreenFader(1.5, False, lambda: setattr(self, "fading", False))
        
    def on_scene_end(self):
        def fade_end():
            setattr(self, "fading", False)
            GameObject.all_objects.clear()

        GameObject.all_objects.clear()
        ScreenFader(1.5, False, lambda: fade_end())
    
    def update(self):
        '''GameObject.update_all()이 불리는 메소드'''

        # 일시정지된 상태여도 fps텍스트는 업데이트
        self.fps_text_renderer.text = str(round(self.app.clock.get_fps()))
        
        # if self.fading:
        #     GameObject.update_all(except_classes=(Entity))
        # else:
        GameObject.update_all()

    def draw(self):
        '''GameObject.update_all()이 불리는 메소드 (paused여도 다 그림.)'''
        GameObject.draw_all()
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
        self.event_bus = EventBus()
        
        self._scene_paused = False
        self.scene_paused = False
        self.app.time_scale = 1

    @property
    def scene_paused(self):
        return self._scene_paused
    
    @scene_paused.setter
    def scene_paused(self, value):
        # 이미 같은 값이면 return
        if self._scene_paused == value:
            return
        
        self._scene_paused = value
        if self._scene_paused == True:
            self.on_pause_start()
            self.app.time_scale = 0
        else:
            self.on_pause_end()
            self.app.time_scale = 1

    def on_pause_start(self):
        pass

    def on_pause_end(self):
        pass
        
    def on_scene_end(self):
        GameObject.all_objects.clear()
    
    def update(self):
        '''GameObject.update_all()이 불리는 메소드'''
        GameObject.update_all()

    def draw(self):
        '''GameObject.update_all()이 불리는 메소드 (paused여도 다 그림.)'''
        GameObject.draw_all()
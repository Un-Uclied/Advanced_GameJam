#외부 라이브러리 임포트
import pygame as pg

class Scene:
    '''씬들의 베이스 클래스'''
    def __init__(self):
        pass

    def scene_enter(self):
        pass

    def scene_exit(self):
        pass
        
    def update(self):
        pass

    def draw(self):
        pass

from .objects import *
from .components import *
from .load_image import *
from .application import *
from .camera import Camera2D

class TestScene(Scene):
    def __init__(self):
        super().__init__()

    def scene_enter(self):
        super().scene_enter()
        # 씬 진입 시 필요한 초기화 작업
        Camera2D.reset()
        
        self.object_a = GameObject.new(GameObject("ObjectA", "statics"))
        self.object_a.position = pg.Vector2(48, 48)

        self.object_b = GameObject.new(GameObject("ObjectB", "statics"), self.object_a)
        self.object_a.local_position = pg.Vector2(0, -48)
        # self.object_b.add_component(SpriteRenderer(load_image(), ))

    def scene_exit(self):
        super().scene_exit()

    def update(self):
        # 씬 업데이트 로직
        GameObject.update_all()

    def draw(self):
        GameObject.draw_all()
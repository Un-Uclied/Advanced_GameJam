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
from .time import Time
from .events import Events
from .camera import Camera2D

class TestScene(Scene):
    def __init__(self):
        super().__init__()

    def scene_enter(self):
        super().scene_enter()
        # 씬 진입 시 필요한 초기화 작업
        Camera2D.reset()
        
        self.object_a = GameObject.new(GameObject("ObjectA", "statics"), pg.Vector2(0, ))
        self.object_a.position = pg.Vector2(48, 48)
        self.object_a.add_component(ObjectDebugger())
        self.object_a.add_component(TextRenderer(self.object_a.name, 12, "blue"))

        self.object_b = GameObject.new(GameObject("ObjectB", "statics"), pg.Vector2(0, ))
        self.object_b.add_component(ObjectDebugger())
        self.object_b.add_component(TextRenderer(self.object_b.name, 12, "blue"))

        self.selected = self.object_a

    def scene_exit(self):
        super().scene_exit()

    def update(self):
        # 씬 업데이트 로직
        GameObject.update_all()

        keys = pg.key.get_pressed()
        if keys[pg.K_a]:
            self.selected.position += pg.Vector2(-Time.delta_time * 100, 0)
        if keys[pg.K_d]:
            self.selected.position += pg.Vector2(Time.delta_time * 100, 0)
        if keys[pg.K_w]:
            self.selected.position += pg.Vector2(0, -Time.delta_time * 100)
        if keys[pg.K_s]:
            self.selected.position += pg.Vector2(0, Time.delta_time * 100)

        for event in Events.events:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_q:
                    self.selected = self.object_a
                elif event.key == pg.K_e:
                    self.selected = self.object_b

        print(Time.fps)

    def draw(self):
        GameObject.draw_all()
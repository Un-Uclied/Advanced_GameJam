#외부 라이브러리 임포트
import pygame as pg

from .camera import Camera2D
from .objects import GameObject
from .time import Time
from .components import *
from .load_image import *

class Scene:
    def __init__(self):
        pass

    def scene_enter(self):
        pass

    def scene_exit(self):
        Camera2D.reset()
        
    def update(self):
        RigidBody.space.step(Time.delta_time)

    def draw(self):
        pass

class TestScene(Scene):
    def __init__(self):
        super().__init__()

    def scene_enter(self):
        super().scene_enter()
        
        self.object_a = GameObject.new(GameObject("ObjectA", "statics"), pg.Vector2(0, 0))
        self.object_a.add_component(ObjectDebugger())
        self.object_a.add_component(TextRenderer(self.object_a.name, 12, "blue"))
        self.object_a.add_component(SpriteRenderer(load_image()))
        self.object_a.add_component(RigidBody(1, self.object_a.get_component(SpriteRenderer).image.get_size(), "box", True, False))
        

        self.object_b = GameObject.new(GameObject("ObjectB", "statics"), pg.Vector2(0, -128))
        self.object_b.add_component(ObjectDebugger())
        self.object_b.add_component(TextRenderer(self.object_b.name, 12, "blue"))
        self.object_b.add_component(RigidBody(1, (64, 64), "box", True, False))

    def scene_exit(self):
        super().scene_exit()

    def update(self):
        super().update()
        GameObject.update_all()
        print(Time.fps)

    def draw(self):
        super().draw()
        GameObject.draw_all()
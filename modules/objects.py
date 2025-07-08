import pygame as pg
import math

class Object:
    all_objects = []
    '''for object in Object.all_objects: #이런 느낌쓰로 간단하게 업뎃 가능 ^^
        object.update()
        object.draw()
    '''
    def __init__(self, position=pg.Vector2(0, 0), rotation=0.0):
        self.position = position
        self.rotation = rotation
        self.components = {}

        Object.all_objects.append(self)

    def add_component(self, comp):
        self.components[type(comp)] = comp
        comp.object = self
        
        if hasattr(comp, "on_start"):
            comp.on_start()

        return comp
    
    def remove_component(self, comp_type):
        comp = self.components.pop(comp_type, None)
        if comp and hasattr(comp, "on_destroy"):
            comp.on_destroy()
        return comp

    def get_component(self, comp_type):
        return self.components.get(comp_type)
    
    def destroy(self):
        for c in self.components.values():
            if hasattr(c, "on_destroy"):
                c.on_destroy()
        Object.all_objects.remove(self)

    def update(self):
        for c in self.components.values():
            if hasattr(c, "update"):
                c.update()

    def draw(self):
        for c in self.components.values():
            if hasattr(c, "draw"):
                c.draw()

    @property
    def right(self) -> pg.Vector2:
        return pg.Vector2(math.cos(self.rotation), -math.sin(self.rotation))

    @property
    def up(self) -> pg.Vector2:
        return pg.Vector2(-math.sin(self.rotation), -math.cos(self.rotation)) #파이게임에선 위로 갈수록 작아져서 뒤집음 ㅇㅇ;

class GameObject(Object):
    def __init__(self, position=pg.Vector2(0, 0), rotation=0.0):
        super().__init__(position=position, rotation=rotation)

class UiObject(Object):
    def __init__(self, position=pg.Vector2(0, 0), rotation=0.0):
        super().__init__(position=position, rotation=rotation)


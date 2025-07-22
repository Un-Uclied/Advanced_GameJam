import pygame as pg

from datas.const import *
from .objects import *

LIGHT_SEGMENTS = 15
LIGHT_FADE_OUT = 10

class Light2D(GameObject):
    light_list : list['Light2D'] = []
    def __init__(self, radius : float, position : pg.Vector2, strength : float = 25):
        super().__init__()
        Light2D.light_list.append(self)

        self.radius : float = radius

        self.position : pg.Vector2 = position
        self.strength = strength

        self._radius_cache = radius #캐싱해서 fps나락을 방지 (빛의 크기가 달라지지 않을때는 새 surface를 안만들어서 연산량 줄이기)
        
        self.make_surface()

    def make_surface(self):
        self.light_surf = pg.Surface([self.radius, self.radius], pg.SRCALPHA)
        
        for i in range(LIGHT_SEGMENTS):
            pg.draw.circle(self.light_surf, pg.Color(0, 0, 0, min(i * self.strength, 255)), [self.radius/2, self.radius/2], self.radius / 2 - i * LIGHT_FADE_OUT)

        self.light_surf = self.app.scene.camera.get_scaled_surface(self.light_surf)

    def on_update(self):
        super().on_update()
        
        if not self._radius_cache == self.radius:
            self.make_surface()

        self._radius_cache = self.radius


    def destroy(self):
        super().destroy()
        Light2D.light_list.remove(self)

class Fog(GameObject):
    def __init__(self, fog_color : pg.Color = pg.Color(80, 80, 80, 240)):
        super().__init__()
        self.fog_color = fog_color

    def on_draw(self):
        self.app.surfaces[LAYER_VOLUME].fill(self.fog_color)

        for light in Light2D.light_list:
            surf = light.light_surf
            pos = self.app.scene.camera.world_to_screen(pg.Vector2(light.position.x - light.radius/2, light.position.y - light.radius/2))
            self.app.surfaces[LAYER_VOLUME].blit(surf, pos, special_flags=pg.BLEND_RGBA_SUB)

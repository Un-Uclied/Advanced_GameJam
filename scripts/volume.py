import pygame as pg

from datas.const import *
from .objects import *

class Light2D(GameObject):
    def __init__(self, radius, position):
        self.radius = radius
        self.position = position
        Fog.light_list.append(self)

    def destroy(self):
        super().destroy()
        Fog.light_list.remove(self)

class Fog(GameObject):
    light_list : list[Light2D] = []
    def __init__(self):
        super().__init__()

    def on_draw(self):
        self.app.surfaces[LAYER_VOLUME].fill("black")
        for light in Fog.light_list:
            light_surface = pg.Surface(light.radius*2, pg.SRCALPHA)
            pg.draw.circle(light_surface, light.radius, (light.radius/2, light.radius/2), light.radius, color=pg.Color(255, 255, 255, 100))
            self.app.surfaces[LAYER_VOLUME].blit(light_surface, light.position, special_flags=pg.BLEND_RGBA_MIN)

import pygame as pg

from scripts.constants import *
from scripts.objects import GameObject

from .light import Light

class Fog(GameObject):
    def __init__(self, fog_color : pg.Color = pg.Color(0, 0, 0, 250)):
        super().__init__()
        self.fog_color = fog_color
        self.fog_surface = pg.Surface(SCREEN_SIZE, flags=pg.SRCALPHA)

    def on_draw(self):
        self.fog_surface.fill((0, 0, 0, 0))

        self.fog_surface.blit(self.app.surfaces[LAYER_OBJ])
        self.fog_surface.blit(self.app.surfaces[LAYER_ENTITY])

        self.fog_surface.fill(self.fog_color, special_flags=pg.BLEND_RGBA_MULT)
        
        Light.draw_lights(self.fog_surface, self.app.scene.camera)

        self.app.surfaces[LAYER_VOLUME].blit(self.fog_surface, (0, 0))
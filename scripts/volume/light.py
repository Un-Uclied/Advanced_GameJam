import pygame as pg

from scripts.constants import *
from scripts.objects import GameObject

LIGHT_SEGMENTS = 15
LIGHT_FADE_OUT = 10

class Light(GameObject):
    all_lights : list["Light"] = []
    def __init__(self, radius, position, strength=25):
        super().__init__()
        self.position = position
        self.radius = radius
        self.make_surface(radius, strength)

        Light.all_lights.append(self)

    def on_destroy(self):
        if self in Light.all_lights:
            Light.all_lights.remove(self)
        super().on_destroy()

    def make_surface(self, radius, strength):
        self.surface = pg.Surface((radius, radius), pg.SRCALPHA)
        for i in range(LIGHT_SEGMENTS):
            alpha = min(i * strength, 255)
            pg.draw.circle(
                self.surface,
                (255, 255, 255, alpha),
                (radius / 2, radius / 2),
                radius / 2 - i * LIGHT_FADE_OUT
            )

    def get_bound_box(self):
        bound_box = pg.Rect(self.position, self.surface.get_size())
        bound_box.center = self.position
        return bound_box

    def on_debug_draw(self):
        super().on_debug_draw()
        camera = self.app.scene.camera

        pg.draw.rect(self.app.surfaces[LAYER_INTERFACE], "yellow", camera.world_rect_to_screen_rect(self.get_bound_box()), width=2)

    @classmethod
    def draw_lights(cls, surface: pg.Surface, camera):
        for light in cls.all_lights:
            box = light.get_bound_box()
            if not camera.is_in_view(box): continue

            screen_rect = camera.world_rect_to_screen_rect(box)
            surface.blit(camera.get_scaled_surface(light.surface), screen_rect.topleft, special_flags=pg.BLEND_RGBA_SUB)
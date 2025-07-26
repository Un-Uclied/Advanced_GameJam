import pygame as pg

from scripts.constants import *
from scripts.objects import GameObject

class AnimatedParticle(GameObject):
    def __init__(self, particle_name : str, position : pg.Vector2, anchor : pg.Vector2 = pg.Vector2(.5, .5)):
        super().__init__()

        self.position = position
        self.anchor = anchor
        self.anim = self.app.ASSETS["animations"]["vfxs"][particle_name].copy()

    def on_update(self):
        super().on_update()
        self.anim.update(self.app.dt)
        if self.anim.done:
            self.on_destroy()

    def on_draw(self):
        camera = self.app.scene.camera
        surface = self.app.surfaces[LAYER_INTERFACE]

        image = self.anim.img()
        screen_pos = camera.world_to_screen(self.position - pg.Vector2(image.get_size()).elementwise() * self.anchor)
        screen_img = camera.get_scaled_surface(image)

        surface.blit(screen_img, screen_pos)

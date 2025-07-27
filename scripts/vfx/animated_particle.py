import pygame as pg

from scripts.constants import *
from scripts.objects import GameObject
from scripts.camera import *

class AnimatedParticle(GameObject):
    def __init__(self, particle_name : str, position : pg.Vector2, anchor : pg.Vector2 = pg.Vector2(.5, .5)):
        super().__init__()

        self.position = position
        self.anchor = anchor

        #파티클 애니메이션 갖고오기
        self.anim = self.app.ASSETS["animations"]["vfxs"][particle_name].copy()

    def update(self):
        super().update()
        self.anim.update(self.app.dt)

        #파티클 애니메이션 끝 자동으로 자기를 없앰
        if self.anim.done:
            self.destroy()

    def draw(self):
        super().draw()
        camera = self.app.scene.camera
        surface = self.app.surfaces[LAYER_DYNAMIC]

        image = self.anim.img()
        screen_pos = CameraMath.world_to_screen(camera, self.position - pg.Vector2(image.get_size()).elementwise() * self.anchor)
        screen_img = CameraView.get_scaled_surface(camera, image)

        surface.blit(screen_img, screen_pos)
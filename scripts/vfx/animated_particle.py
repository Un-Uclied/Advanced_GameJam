import pygame as pg

from scripts.constants import *
from scripts.camera import *

from scripts.objects import GameObject

class AnimatedParticle(GameObject):
    """
    애니메이션 기반 파티클 이펙트 객체

    :param particle_name: 파티클 애니메이션 에셋 이름 (예: 'explosion', 'sparkle' 등)
    :param position: 월드 기준 파티클 생성 위치 (주로 엔티티 중심)
    :param anchor: 이미지 기준 앵커 위치, 기본값은 (0.5, 0.5)로 중앙 기준

    파티클 애니메이션이 끝나면 자동으로 제거됨.
    """

    def __init__(self, particle_name: str, position: pg.Vector2, anchor: pg.Vector2 = pg.Vector2(.5, .5)):
        super().__init__()

        self.position = position
        self.anchor = anchor

        # 파티클 애니메이션 갖고오기
        self.anim = self.app.ASSETS["animations"]["vfxs"][particle_name].copy()

    def update(self):
        super().update()
        self.anim.update(self.app.dt)

        # 파티클 애니메이션 끝나면 자기 자신 제거
        if self.anim.done:
            self.destroy()

    def draw(self):
        super().draw()
        camera = self.app.scene.camera
        surface = self.app.surfaces[LAYER_DYNAMIC]

        image = self.anim.img()
        screen_pos = CameraMath.world_to_screen(
            camera,
            self.position - pg.Vector2(image.get_size()).elementwise() * self.anchor
        )
        screen_img = CameraView.get_scaled_surface(camera, image)

        surface.blit(screen_img, screen_pos)
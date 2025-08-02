import pygame as pg


from scripts.ai import WanderAI

from scripts.vfx import Outline, AnimatedParticle
from scripts.volume import Light

HIT_BOX_SIZE = (40, 50)

MOVE_SPEED = 1.5
MIN_CHANGE_TIMER = .8
MAX_CHANGE_TIMER = 1.5

FLIP_OFFSET = {
    False: pg.Vector2(5, -20),
    True: pg.Vector2(5, -20)
}

from .base import PhysicsEntity
class Soul(PhysicsEntity):
    def __init__(self, spawn_position : pg.Vector2):
        self.outline = Outline(self, "red")

        super().__init__("soul", pg.Rect(spawn_position, HIT_BOX_SIZE))

        self.ai = WanderAI(self, MIN_CHANGE_TIMER, MAX_CHANGE_TIMER)

        self.flip_offset = FLIP_OFFSET

        self.light = Light(250, pg.Vector2(self.rect.center))
        self.light_follow_speed = 5

        self.collect_particle_anim = self.app.ASSETS["animations"]["vfxs"]["soul"]["interact"]

    def destroy(self):
        # 자기가 생성한 빛, 아웃라인도 직접 제거
        self.light.destroy()
        self.outline.destroy()

        # 파티클 생성, 소리 재생, 카메라 흔들림
        AnimatedParticle(self.collect_particle_anim, pg.Vector2(self.rect.center))
        self.app.sound_manager.play_sfx(self.app.ASSETS["sounds"]["soul"]["interact"])
        self.app.scene.camera.shake_amount += 10

        super().destroy()

    def follow_light(self):
        self.light.position = self.light.position.lerp(self.rect.center, max(min(self.app.dt * self.light_follow_speed, 1), 0))

    def handle_input(self):
        for event in self.app.events:
            ps = self.app.scene.player_status
            pc = ps.player_character
            if event.type == pg.KEYDOWN and event.key == pg.K_e and self.rect.colliderect(pc.rect):
                self.destroy()

    def update(self):
        super().update()
        self.ai.update()
        self.velocity.x = self.ai.direction.x * MOVE_SPEED * 100
        self.follow_light()
        self.handle_input()
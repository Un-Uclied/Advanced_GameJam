import pygame as pg


from scripts.ai import *
from scripts.vfx import *
from scripts.volume import *
from scripts.ui import *
from scripts.core import *
from .base import PhysicsEntity

HIT_BOX_SIZE = (40, 50)

MOVE_SPEED = 1.5
MIN_CHANGE_TIMER = .8
MAX_CHANGE_TIMER = 1.5

FLIP_OFFSET = {
    False: pg.Vector2(5, -20),
    True: pg.Vector2(5, -20)
}

class Soul(PhysicsEntity):
    def __init__(self, spawn_position : pg.Vector2):
        super().__init__("soul", pg.Rect(spawn_position, HIT_BOX_SIZE))

        self.ai = WanderAI(self, MIN_CHANGE_TIMER, MAX_CHANGE_TIMER)

        self.flip_offset = FLIP_OFFSET

        self.light = Light(250, pg.Vector2(self.rect.center))
        self.light_follow_speed = 5

        self.collect_particle_anim = self.app.ASSETS["animations"]["vfxs"]["soul"]["interact"]

        # 힌트 UI
        self.hint_ui = TextRenderer("[E]", pg.Vector2(self.rect.centerx, self.rect.top - 30), font_size=12, anchor=pg.Vector2(0.5, 1.0), use_camera=True)
        self.hint_ui.alpha = 0

        # 내부 상태
        self.player_was_inside = False
        self.current_tween = None

    def destroy(self):
        # 자기가 생성한 빛도 직접 제거
        self.light.destroy()
        self.hint_ui.destroy()

        # 파티클 생성, 소리 재생, 카메라 흔들림
        AnimatedParticle(self.collect_particle_anim, pg.Vector2(self.rect.center))
        self.app.sound_manager.play_sfx(self.app.ASSETS["sounds"]["soul"]["interact"])
        self.app.scene.camera.shake_amount += 10

        super().destroy()

    def follow_light(self):
        self.light.position = self.light.position.lerp(self.rect.center, max(min(self.app.dt * self.light_follow_speed, 1), 0))

    def handle_input(self):
        if not hasattr(self.app.scene, "player_status") or not hasattr(self.app.scene.player_status, "player_character"):
            return
    
        ps = self.app.scene.player_status
        pc = ps.player_character
        
        for event in self.app.events:
            if event.type == pg.KEYDOWN and event.key == pg.K_e and self.rect.colliderect(pc.rect):
                self.destroy()

    def handle_hint_ui(self):
        if not hasattr(self.app.scene, "player_status") or not hasattr(self.app.scene.player_status, "player_character"):
            return
    
        self.hint_ui.pos = pg.Vector2(self.rect.centerx, self.rect.top - 30)

        ps = self.app.scene.player_status
        pc = ps.player_character
        is_inside = self.rect.colliderect(pc.rect)
        # 들어온 순간 한번
        if is_inside and not self.player_was_inside:
            # 기존 Tween 제거
            if self.current_tween:
                self.current_tween.destroy()

            # 새 Tween 생성
            self.current_tween = Tween(self.hint_ui, "alpha", self.hint_ui.alpha, 255, 0.3)
            self.player_was_inside = True

        # 나간 순간 한번
        elif not is_inside and self.player_was_inside:
            if self.current_tween:
                self.current_tween.destroy()
            self.current_tween = Tween(self.hint_ui, "alpha", self.hint_ui.alpha, 0, 0.3)
            self.player_was_inside = False

    def update(self):
        super().update()
        self.ai.update()
        self.velocity.x = self.ai.direction.x * MOVE_SPEED * 100
        self.follow_light()
        self.handle_input()
        self.handle_hint_ui()
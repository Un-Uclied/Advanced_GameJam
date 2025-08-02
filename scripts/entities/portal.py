import pygame as pg
from scripts.ui import TextRenderer
from scripts.vfx import *

HIT_BOX_SIZE = (180, 165)
LIGHT_SIZE = 500

from .base import Entity

class Portal(Entity):
    def __init__(self, spawn_position: pg.Vector2):
        rect = pg.Rect(spawn_position, HIT_BOX_SIZE)
        super().__init__("portal", rect)

        # 포탈 빛 생성
        from scripts.volume import Light
        self.light = Light(LIGHT_SIZE, pg.Vector2(self.rect.center))

        self.interacted = False
        self.interact_sound = self.app.ASSETS["sounds"]["portal"]["interact"]
        self.interact_particle_anim = self.app.ASSETS["animations"]["vfxs"]["portal"]["interact"]

        # 힌트 UI
        self.hint_ui = TextRenderer("F키로 균열 진입", pg.Vector2(self.rect.centerx, self.rect.top - 30), anchor=pg.Vector2(0.5, 1.0), use_camera=True)
        self.hint_ui.alpha = 0

        # 내부 상태
        self.player_was_inside = False
        self.current_tween = None

    def update(self):
        super().update()

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

        # 인터랙션
        if is_inside and not self.interacted:
            for event in self.app.events:
                if event.type == pg.KEYDOWN and event.key == pg.K_f:
                    self.app.scene.on_level_end()
                    self.app.sound_manager.play_sfx(self.interact_sound)
                    AnimatedParticle(self.interact_particle_anim, pg.Vector2(self.rect.center))
                    self.app.scene.camera.shake_amount += 25
                    self.interacted = True
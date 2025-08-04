import pygame as pg
import random

from scripts.ai import *
from scripts.vfx import *
from scripts.constants import *
from scripts.volume import *
from scripts.ui import *
from scripts.core import *
from .base import PhysicsEntity

HIT_BOX_SIZE = (40, 50)

MOVE_SPEED = 1
MIN_CHANGE_TIMER = .8
MAX_CHANGE_TIMER = 1.5

LIGHT_SIZE = 300
LIGHT_STRENGTH = 30

FLIP_OFFSET = {
    False: pg.Vector2(5, -20),
    True: pg.Vector2(5, -20)
}

class Soul(PhysicsEntity):
    def __init__(self, spawn_position : pg.Vector2):
        super().__init__("soul", pg.Rect(spawn_position, HIT_BOX_SIZE))

        self.ai = WanderAI(self, MIN_CHANGE_TIMER, MAX_CHANGE_TIMER)

        self.flip_offset = FLIP_OFFSET

        self.light = Light(LIGHT_SIZE, pg.Vector2(self.rect.center), LIGHT_STRENGTH)
        self.light_follow_speed = 5

        # player_status가 없으면 플레이어가 없는것으로 간주, 타입은 디폴트
        if hasattr(self.app.scene, "player_status"):
            self.soul_type = random.choice(ALL_SOUL_TYPES)
            self.type_icon_image = ImageRenderer(self.app.ASSETS["ui"]["soul_icons"][self.soul_type], pg.Vector2(self.rect.center) + pg.Vector2(0, self.rect.h / 2), anchor=pg.Vector2(.5, 0), use_camera=True)
        else:
            self.soul_type = SOUL_DEFAULT
            self.type_icon_image = None

        # 힌트 UI
        self.hint_ui = TextRenderer(f"[E] {self.soul_type}", pg.Vector2(self.rect.centerx, self.rect.top - 30), anchor=pg.Vector2(0.5, 1.0), use_camera=True)
        self.hint_ui.alpha = 0

        # 내부 상태
        self.player_was_inside = False
        self.current_tween = None

        self.collect_particle_anim = self.app.ASSETS["animations"]["vfxs"]["soul"]["interact"]

    def destroy(self):
        # 자기가 생성한 오브젝트들 직접 제거
        self.light.destroy()
        if self.type_icon_image is not None:
            self.type_icon_image.destroy()
        self.hint_ui.destroy()

        # 파티클 생성, 소리 재생, 카메라 흔들림
        AnimatedParticle(self.collect_particle_anim, pg.Vector2(self.rect.center))
        self.app.sound_manager.play_sfx(self.app.ASSETS["sounds"]["soul"]["interact"])
        self.app.scene.camera.shake_amount += 10

        self.app.scene.event_bus.emit("on_soul_interact", self.soul_type)

        super().destroy()

    def follow_objects(self):
        self.light.position = self.light.position.lerp(self.rect.center, max(min(self.app.dt * self.light_follow_speed, 1), 0))
        if self.type_icon_image is not None:
            self.type_icon_image.pos = pg.Vector2(self.rect.center) + pg.Vector2(0, self.rect.h / 2)

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
        self.follow_objects()
        self.handle_input()
        self.handle_hint_ui()
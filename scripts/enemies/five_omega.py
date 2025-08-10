import pygame as pg
import random
import math

from scripts.core import *
from scripts.attacks import *
from scripts.vfx import *
from scripts.constants import *
from .base import *
from scripts.status import *
from scripts.ai import *
from scripts.projectiles import *

HIT_BOX_SIZE = (100, 256)
FLIP_OFFSET = {
    False : [-165, -25],
    True  : [-125, -25]
}

MAX_HEALTH = 2500
MIN_CHANGE_TIMER = 0.1
MAX_CHANGE_TIMER = 1.2

COLLIDE_ATTACK_DAMAGE = 5

# ---------------------------
# 보스 패턴 베이스 클래스
# ---------------------------
class BossPattern:
    PATTERN_INTERVAL = 1.0  # 확률 체크 간격 (초)

    def __init__(self, boss: "FiveOmega", enabled=False):
        self.boss = boss
        self.app = boss.app
        self.enabled = enabled
        self.cooltime = None
        self._pattern_timer = Timer(BossPattern.PATTERN_INTERVAL, auto_destroy=False)

    def start(self): pass
    def end(self): pass
    def on_enabled_update(self): pass

    def on_disabled_update(self):
        """
        비활성 상태에서 주기적으로 확률 체크해서 패턴 시작 여부 결정
        """
        if not self.boss.registered_patterns["wander"].enabled:
            return
        if self.cooltime and self.cooltime.current_time > 0:
            return
        if self._pattern_timer.current_time > 0:
            return

        self._pattern_timer.reset()

        if self.should_start_pattern():
            self._disable_other_patterns()
            self.start()

    def should_start_pattern(self) -> bool:
        """
        패턴 시작 확률 체크 (서브클래스에서 PATTERN_PERCENT 참고)
        """
        return int(random.random() * 100) <= getattr(self, "PATTERN_PERCENT", 0)

    def _disable_other_patterns(self):
        for pattern in self.boss.registered_patterns.values():
            if pattern is not self:
                pattern.enabled = False

# ---------------------------
# 낫 공격 패턴
# ---------------------------
class ScythePattern(BossPattern):
    SCYTHE_ATTACK_TRIGGER_RANGE = 220
    SCYTHE_ATTACK_DAMAGE = 20
    SCYTHE_ATTACK_WIDTH = 180
    SCYTHE_ATTACK_COOLTIME = 3
    PATTERN_PERCENT = 80

    def __init__(self, boss):
        super().__init__(boss)
        self.cooltime = Timer(self.SCYTHE_ATTACK_COOLTIME, auto_destroy=False)
        self.scythe_attack_sound = self.app.ASSETS["sounds"]["enemy"]["boss"]["scythe"]
        self.explosion_particle_anim = self.app.ASSETS["animations"]["vfxs"]["explosion"]

    def start(self):
        self.enabled = True
        self.cooltime.reset()
        self.boss.set_action("scythe_attack")

        self.app.scene.camera.shake_amount += 30
        self.app.sound_manager.play_sfx(self.scythe_attack_sound)

        effect_pos = self.boss.rect.topleft if self.boss.velocity.x < 0 else self.boss.rect.center
        AnimatedParticle(self.explosion_particle_anim, pg.Vector2(effect_pos))

        damage_rect = self.boss.rect.copy()
        damage_rect.w = self.SCYTHE_ATTACK_WIDTH
        damage_rect.x += self.boss.rect.w if self.boss.velocity.x > 0 else -self.SCYTHE_ATTACK_WIDTH
        DamageArea(damage_rect, self.SCYTHE_ATTACK_DAMAGE, 0.45, once=True)

        Timer(0.85, self.end)

    def end(self):
        self.enabled = False
        self.boss.set_action("idle")
        self.boss.registered_patterns["wander"].enabled = True

    def on_disabled_update(self):
        # 플레이어가 앞에 있고 가까이 있으면 패턴 시작 고려
        direction = self.app.scene.player_status.player_character.get_direction_from(pg.Vector2(self.boss.rect.center))
        distance = self.app.scene.player_status.player_character.get_distance_from(pg.Vector2(self.boss.rect.center))
        my_direction = pg.Vector2(-1 if self.boss.anim.flip_x else 1, 0)

        if direction.dot(my_direction) > 0:  # 플레이어가 반대
            return
        if distance >= self.SCYTHE_ATTACK_TRIGGER_RANGE:
            return

        super().on_disabled_update()

# ---------------------------
# 눈 레이저 공격 패턴
# ---------------------------
class EyePattern(BossPattern):
    EYE_ATTACK_COOLTIME = 1
    EYE_ATTACK_TIME = 10
    EYE_ATTACK_SPEED = 0.1
    EYE_ATTACK_DELAY = 3
    PATTERN_PERCENT = 30

    def __init__(self, boss):
        super().__init__(boss)
        self.cooltime = Timer(self.EYE_ATTACK_COOLTIME, auto_destroy=False)
        self.bullet_timer = Timer(self.EYE_ATTACK_SPEED, auto_destroy=False)
        self.can_lazer = False

    def _attack_projectile(self):
        if self.bullet_timer.current_time > 0:
            return
        self.bullet_timer.reset()
        my_direction = pg.Vector2(1 if self.boss.anim.flip_x else -1, 0)
        LazerBoss(pg.Vector2(self.boss.rect.center) + pg.Vector2(0, 30), my_direction)

    def start(self):
        self.enabled = True
        self.cooltime.reset()
        self.boss.set_action("turn_eye")

        def attack_start():
            self.app.sound_manager.play_sfx(self.app.ASSETS["sounds"]["enemy"]["boss"]["lazer"])
            Timer(2.25, lambda: setattr(self, "can_lazer", True))
            Timer(self.EYE_ATTACK_TIME, self.end)

        Timer(self.EYE_ATTACK_DELAY, attack_start)

    def on_enabled_update(self):
        if self.can_lazer:
            self._attack_projectile()
            self.app.scene.camera.shake_amount = 25

    def end(self):
        self.enabled = False
        self.can_lazer = False
        self.boss.set_action("idle")
        self.boss.registered_patterns["wander"].enabled = True

# ---------------------------
# 총알 회전 발사 패턴
# ---------------------------
class ProjectilePattern(BossPattern):
    PROJECTILE_ATTACK_COOLTIME = 2.5
    PROJECTILE_ATTACK_TIME = 2
    PROJECTILE_ATTACK_SPEED = 0.15
    PATTERN_PERCENT = 25
    ROTATE_SPEED = 200

    def __init__(self, boss):
        super().__init__(boss)
        self.cooltime = Timer(self.PROJECTILE_ATTACK_COOLTIME, auto_destroy=False)
        self.bullet_timer = Timer(self.PROJECTILE_ATTACK_SPEED, auto_destroy=False)
        self.should_rotate_to_right = True

    def _attack_projectile(self):
        if self.bullet_timer.current_time > 0:
            return
        self.bullet_timer.reset()

        pos = self.app.scene.tilemap.get_pos_by_data("custom_point", 0)[0]

        direction = pg.Vector2(
            math.cos(math.radians(self.current_angle)),
            -math.sin(math.radians(self.current_angle))
        )

        ProjectileBoss(pos, direction)

    def _update_rotation(self):
        if self.should_rotate_to_right:
            self.current_angle += self.app.dt * self.ROTATE_SPEED
            if self.current_angle > 0:
                self.current_angle = 0
                self.should_rotate_to_right = False
        else:
            self.current_angle -= self.app.dt * self.ROTATE_SPEED
            if self.current_angle < -180:
                self.current_angle = -180
                self.should_rotate_to_right = True

    def start(self):
        self.enabled = True
        self.cooltime.reset()
        Timer(self.PROJECTILE_ATTACK_TIME, self.end)
        self.current_angle = -180

    def on_enabled_update(self):
        self._attack_projectile()
        self._update_rotation()

    def end(self):
        self.enabled = False
        self.boss.registered_patterns["wander"].enabled = True

# ---------------------------
# 기본 이동 패턴 (워든)
# ---------------------------
class WanderPattern(BossPattern):
    MOVE_SPEED = 2
    DIRECTION_OVERRIDE_RANGE = 500

    def __init__(self, boss, enabled=True):
        super().__init__(boss, enabled)
        self.is_overriding = False
        self.is_moving = False

    def on_enabled_update(self):
        direction = self.app.scene.player_status.player_character.get_direction_from(pg.Vector2(self.boss.rect.center))
        distance = self.app.scene.player_status.player_character.get_distance_from(pg.Vector2(self.boss.rect.center))
        self.is_overriding = distance < self.DIRECTION_OVERRIDE_RANGE

        self.is_moving = False
        if self.is_overriding:
            x_direction = 1 if direction.x > 0 else -1
            self.is_moving = True
        else:
            x_direction = self.boss.ai.direction.x
            if x_direction != 0:
                self.is_moving = True

        self.boss.velocity.x = x_direction * (
            (self.MOVE_SPEED + ENEMY_EVIL_A_SPEED_UP)
            if self.boss.status.soul_type == SOUL_EVIL_A
            else self.MOVE_SPEED
        ) * 100

# ---------------------------
# 보스 본체 클래스
# ---------------------------
class FiveOmega(PhysicsEnemy):
    def __init__(self, spawn_position: pg.Vector2):
        super().__init__(
            name="five_omega",
            rect=pg.Rect(spawn_position, HIT_BOX_SIZE),
            collide_attack_damage=COLLIDE_ATTACK_DAMAGE,
        )

        self.flip_offset = FLIP_OFFSET
        self.status = EnemyStatus(self, MAX_HEALTH)
        self.ai = WanderAI(self, MIN_CHANGE_TIMER, MAX_CHANGE_TIMER)

        self.registered_patterns = {
            "wander": WanderPattern(self, True),
            "scythe": ScythePattern(self),
            "projectile": ProjectilePattern(self),
            "eye" : EyePattern(self)
        }

    def _update_patterns(self):
        """
        패턴들 랜덤 순서로 업데이트 (활성화/비활성화에 따라)
        """
        patterns = list(self.registered_patterns.values())
        random.shuffle(patterns)
        for pattern in patterns:
            if pattern.enabled:
                pattern.on_enabled_update()
            else:
                pattern.on_disabled_update()

    def update(self):
        super().update()
        self.ai.update()
        self._update_patterns()
        self._control_animation()

    def _control_animation(self):
        wander = self.registered_patterns["wander"]
        if wander.enabled:
            if wander.is_moving:
                self.set_action("run")
            else:
                self.set_action("idle")
import pygame as pg
import random
import math

from scripts.utils import *
from scripts.attacks import *
from scripts.vfx import *
from scripts.constants import *
from scripts.status import *
from scripts.volume import *
from scripts.entities import *
from scripts.enemies import *
from scripts.ai import *
from scripts.projectiles import *
from scripts.ui import *
from .base import *

HIT_BOX_SIZE = (100, 256)
FLIP_OFFSET = {
    False : [-165, -25],
    True  : [-125, -25]
}

MAX_HEALTH = 3500
MIN_CHANGE_TIMER = 0.1
MAX_CHANGE_TIMER = 0.8

COLLIDE_ATTACK_DAMAGE = 15

# ---------------------------
# 보스 패턴 베이스 클래스
# ---------------------------
class BossPattern:
    PATTERN_INTERVAL = .5 # 확률 체크 간격 (초)

    def __init__(self, boss: "FiveOmega", enabled=False):
        self.boss = boss
        self.app = boss.app
        self.scene = boss.app.scene
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
        if self.cooltime and self.cooltime.get_time() > 0:
            return
        if self._pattern_timer.get_time() > 0:
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
    COOLDOWN = 3
    TRIGGER_RANGE = 220
    DAMAGE = 20
    ATTACK_WIDTH = 180
    PATTERN_PERCENT = 80
    DAMAGE_DURATION = 0.45
    END_DELAY = 0.85

    def __init__(self, boss):
        super().__init__(boss)
        self.cooltime = Timer(self.COOLDOWN, auto_destroy=False)
        self.attack_sfx = self.app.ASSETS["sounds"]["enemy"]["boss"]["scythe"]
        self.explosion_anim = self.app.ASSETS["animations"]["vfxs"]["explosion"]

    def start(self):
        self.enabled = True
        self.cooltime.reset()
        self.boss.set_action("scythe_attack")

        # 카메라 흔들림 & 효과음
        self.scene.camera.shake_amount += 30
        self.app.sound_manager.play_sfx(self.attack_sfx)

        # 폭발 이펙트 위치 계산
        effect_pos = self.boss.rect.topleft if self.boss.velocity.x < 0 else self.boss.rect.center
        AnimatedParticle(self.explosion_anim, pg.Vector2(effect_pos))

        # 데미지 영역 설정 (낫 휘두르는 범위)
        damage_rect = self.boss.rect.copy()
        damage_rect.w = self.ATTACK_WIDTH
        damage_rect.x += self.boss.rect.w if self.boss.velocity.x > 0 else -self.ATTACK_WIDTH

        DamageArea(damage_rect, self.DAMAGE, self.DAMAGE_DURATION, once=True)

        # 공격 끝내기 타이머
        Timer(self.END_DELAY, self.end)

    def end(self):
        self.enabled = False
        self.boss.set_action("idle")
        self.boss.registered_patterns["wander"].enabled = True

    def on_disabled_update(self):
        player = self.scene.player_status.player_character
        boss_center = pg.Vector2(self.boss.rect.center)
        direction_to_player = player.get_direction_from(boss_center)
        distance_to_player = player.get_distance_from(boss_center)

        # 플레이어가 뒤쪽에 있거나 너무 멀면 공격 안 함
        boss_facing_dir = pg.Vector2(-1 if self.boss.anim.flip_x else 1, 0)
        if direction_to_player.dot(boss_facing_dir) > 0:
            return
        if distance_to_player >= self.TRIGGER_RANGE:
            return

        super().on_disabled_update()

# ---------------------------
# 눈 레이저 공격 패턴
# ---------------------------
class EyePattern(BossPattern):
    COOLDOWN = 20
    ATTACK_DURATION = 10
    FIRE_INTERVAL = 0.1
    ATTACK_DELAY = 3
    LAZER_START_DELAY = 2.25
    PATTERN_PERCENT = 15
    CAMERA_SHAKE = 25
    
    CO_PATTERNS = ("knife", "projectile")
    CO_PATTERN_PERCENT = 100

    def __init__(self, boss):
        super().__init__(boss)
        self.cooltime = Timer(self.COOLDOWN, auto_destroy=False)
        self.fire_timer = Timer(self.FIRE_INTERVAL, auto_destroy=False)
        self.can_lazer = False

    def start(self):
        if self.enabled:
            return
        self.enabled = True
        self.cooltime.reset()
        self.boss.set_action("turn_eye")

        # 레이저 공격 시작 예약
        Timer(self.ATTACK_DELAY, self._prepare_lazer)

    def _prepare_lazer(self):
        self.app.sound_manager.play_sfx(self.app.ASSETS["sounds"]["enemy"]["boss"]["lazer"])
        def lazer_start():
            self.can_lazer = True
            # 버그 많아서 아 포기포기
            # if int(random.random() * 100) <= EyePattern.CO_PATTERN_PERCENT:
            #     target_pattern = random.choice(EyePattern.CO_PATTERNS)
            #     self.boss.registered_patterns[target_pattern].start()
        Timer(self.LAZER_START_DELAY, lambda: lazer_start())
        Timer(self.ATTACK_DURATION, self.end)

    def on_enabled_update(self):
        if self.can_lazer:
            self._try_fire()
            self.scene.camera.shake_amount = self.scene.camera_SHAKE
        self.boss.registered_patterns["wander"].enabled = False

    def _try_fire(self):
        if self.fire_timer.get_time() > 0:
            return
        self.fire_timer.reset()

        direction = pg.Vector2(1 if self.boss.anim.flip_x else -1, 0)
        spawn_pos = pg.Vector2(self.boss.rect.center) + pg.Vector2(0, 30)
        if hasattr(self.scene, "player_status"):
            LazerBoss(spawn_pos, direction)

    def end(self):
        self.enabled = False
        self.can_lazer = False
        self.boss.set_action("idle")
        self.boss.registered_patterns["wander"].enabled = True

# ---------------------------
# 총알 회전 발사 패턴
# ---------------------------
class ProjectilePattern(BossPattern):
    COOLDOWN = 6
    ATTACK_DURATION = 2
    FIRE_INTERVAL = 0.15
    ROTATE_SPEED = 200
    START_ANGLE = -180
    END_ANGLE = 0
    PATTERN_PERCENT = 40

    def __init__(self, boss):
        super().__init__(boss)
        self.cooltime = Timer(self.COOLDOWN, auto_destroy=False)
        self.fire_timer = Timer(self.FIRE_INTERVAL, auto_destroy=False)
        self.rotate_right = True
        self.current_angle = self.START_ANGLE

    def start(self):
        self.enabled = True
        self.cooltime.reset()
        self.current_angle = self.START_ANGLE
        Timer(self.ATTACK_DURATION, self.end)

    def on_enabled_update(self):
        self._try_fire()
        self._rotate()

    def _try_fire(self):
        if self.fire_timer.get_time() > 0:
            return
        self.fire_timer.reset()

        spawn_pos = self._get_spawn_position()
        direction = self._get_direction_from_angle(self.current_angle)
        if hasattr(self.scene, "player_status"):
            FireBoss(spawn_pos, direction)

    def _rotate(self):
        delta = self.app.dt * self.ROTATE_SPEED
        if self.rotate_right:
            self.current_angle += delta
            if self.current_angle >= self.END_ANGLE:
                self.current_angle = self.END_ANGLE
                self.rotate_right = False
        else:
            self.current_angle -= delta
            if self.current_angle <= self.START_ANGLE:
                self.current_angle = self.START_ANGLE
                self.rotate_right = True

    def _get_spawn_position(self):
        return self.scene.tilemap_data.get_positions_by_types("custom_point", 0)[0]

    def _get_direction_from_angle(self, angle):
        rad = math.radians(angle)
        return pg.Vector2(math.cos(rad), -math.sin(rad))

    def end(self):
        self.enabled = False
        self.boss.registered_patterns["wander"].enabled = True

# ---------------------------
# 칼날 발사 패턴
# ---------------------------
class KnifePattern(BossPattern):
    COOLDOWN = 3.5
    SHOW_TIME = .4
    ATTACK_DELAY = .15
    FIRE_OFFSET = pg.Vector2(0, 1000)
    LINE_THICKNESS = 2
    PATTERN_PERCENT = 40

    def __init__(self, boss):
        super().__init__(boss)
        self.cooltime = Timer(self.COOLDOWN, auto_destroy=False)

        assets = self.app.ASSETS["sounds"]["enemy"]["boss"]
        self.sfx_warn = assets["knife_warn"]
        self.sfx_throw = assets["knife_throw"]

        self.warning_lines = []
        self.attack_targets = []

    def start(self):
        self.enabled = True
        self.cooltime.reset()
        self.scene.camera.shake_amount += 20

        start_positions = self._get_start_positions()
        self.warning_lines = [
            LineWarning(pos - self.FIRE_OFFSET, pg.Vector2(), self.LINE_THICKNESS)
            for pos in start_positions
        ]
        self.attack_targets = [pg.Vector2() for _ in start_positions]

        self.app.sound_manager.play_sfx(self.sfx_warn)
        Timer(self.SHOW_TIME, self._attack_start)

    def _attack_start(self):
        for line in self.warning_lines:
            line.destroy()
        self.warning_lines.clear()
        Timer(self.ATTACK_DELAY, self._attack)

    def _attack(self):
        self.app.sound_manager.play_sfx(self.sfx_throw)
        self.scene.camera.shake_amount += 50

        for start_pos, target in zip(self._get_start_positions(), self.attack_targets):
            start_pos -= self.FIRE_OFFSET
            direction = target - start_pos
            if direction.length_squared() > 0:
                direction.normalize_ip()
            if hasattr(self.scene, "player_status"):
                KnifeBoss(start_pos, direction)

        self.end()

    def on_enabled_update(self):
        player_center = pg.Vector2(self.scene.player_status.player_character.rect.center)
        for i, line in enumerate(self.warning_lines):
            line.end = player_center
            self.attack_targets[i] = player_center

    def _get_start_positions(self):
        return self.scene.tilemap_data.get_positions_by_types("custom_point", 1)

    def end(self):
        self.enabled = False
        self.boss.registered_patterns["wander"].enabled = True

# ---------------------------
# 잡몹 스폰 패턴
# ---------------------------
class SpawnPattern(BossPattern):
    COOLDOWN = 2
    PATTERN_PERCENT = 80
    SPAWN_POS_OFFSET = pg.Vector2(0, -500)
    CAN_SPAWN_CLASS = (OneBeta, TwoBeta, FourBeta)

    def __init__(self, boss):
        super().__init__(boss)
        self.cooltime = Timer(self.COOLDOWN, auto_destroy=False)

        self.spawn_sound = self.app.ASSETS["sounds"]["enemy"]["boss"]["spawn"]

    def start(self):
        self.enabled = True
        self.cooltime.reset()
        self.scene.camera.shake_amount += 20

        spawn_position = random.choice(self._get_start_positions())
        spawn_class = random.choice(self.CAN_SPAWN_CLASS)
        spawn_class(spawn_position + self.SPAWN_POS_OFFSET)

        self.end()

    def on_enabled_update(self):
        player_center = pg.Vector2(self.scene.player_status.player_character.rect.center)
        for i, line in enumerate(self.warning_lines):
            line.end = player_center
            self.attack_targets[i] = player_center

    def _get_start_positions(self):
        return self.scene.tilemap_data.get_positions_by_types("custom_point", 1)

    def end(self):
        self.enabled = False
        self.boss.registered_patterns["wander"].enabled = True

# ---------------------------
# 기본 이동 패턴
# ---------------------------
class WanderPattern(BossPattern):
    MOVE_SPEED = 2
    DIRECTION_OVERRIDE_RANGE = 700

    def __init__(self, boss, enabled=True):
        super().__init__(boss, enabled)
        self.is_overriding = False
        self.is_moving = False

    def on_enabled_update(self):
        direction = self.scene.player_status.player_character.get_direction_from(pg.Vector2(self.boss.rect.center))
        distance = self.scene.player_status.player_character.get_distance_from(pg.Vector2(self.boss.rect.center))
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
    PHASES = [
        {"name": "phase_1", "health_threshold": 1.0},  # 100%
        {"name": "phase_2", "health_threshold": 0.5},  # 50%
        {"name": "phase_3", "health_threshold": 0.25},  # 25%
    ]

    def __init__(self, spawn_position: pg.Vector2):
        """
        FiveOmega 클래스의 생성자.

        Args:
            spawn_position (pg.Vector2): 몬스터가 생성될 초기 위치.
        """
        super().__init__(
            name="five_omega",
            rect=pg.Rect(spawn_position, HIT_BOX_SIZE),
            collide_attack_damage=COLLIDE_ATTACK_DAMAGE,
        )
        self.flip_offset = FLIP_OFFSET
        self.status = EnemyStatus(self, MAX_HEALTH)
        self.ai = WanderAI(self, MIN_CHANGE_TIMER, MAX_CHANGE_TIMER)

        self.current_phase_index = 0
        self.registered_patterns = {
            "wander": WanderPattern(self, True),
            "scythe": ScythePattern(self),
            "projectile": ProjectilePattern(self),
            "knife": KnifePattern(self),
            "eye": EyePattern(self),
        }

        # 페이즈별 시작/업데이트 메서드 맵
        self.phase_start_handlers = {
            "phase_1": self.phase_1_start,
            "phase_2": self.phase_2_start,
            "phase_3": self.phase_3_start,
        }
        self.phase_update_handlers = {
            "phase_1": self.phase_1_update,
            "phase_2": self.phase_2_update,
            "phase_3": self.phase_3_update,
        }

        # 초기 페이즈 시작 이벤트 호출
        self.trigger_phase_start()

    def trigger_phase_start(self):
        """
        현재 페이즈에 해당하는 시작 핸들러 메서드를 호출.
        """
        phase_name = self.PHASES[self.current_phase_index]["name"]
        start_handler = self.phase_start_handlers.get(phase_name)
        if start_handler:
            start_handler()

    def check_phase(self):
        """
        현재 체력에 따라 페이즈가 변경되었는지 확인.
        변경되었으면 새로운 페이즈 시작 이벤트를 트리거.
        """
        health_ratio = self.status.health / self.status.max_health
        next_phase_index = self.current_phase_index

        # 다음 페이즈 조건 검사
        for i in range(self.current_phase_index + 1, len(self.PHASES)):
            if health_ratio <= self.PHASES[i]["health_threshold"]:
                next_phase_index = i
            else:
                break

        if next_phase_index != self.current_phase_index:
            self.current_phase_index = next_phase_index
            self.trigger_phase_start()

    def phase_1_start(self):
        """
        페이즈 1 시작 시 처리할 로직. (딱히 없음.)
        """
        pass

    def phase_2_start(self):
        """
        페이즈 2 시작 시 처리할 로직.
        모든 라이트를 제거하고, 화면을 흔들고, 효과음과 파티클 효과를 재생.
        플레이어에게 고정된 새로운 라이트를 생성.
        """
        lights = self.scene.get_objects_by_types(Light)
        for light in lights[:]:
            light.destroy()
        self.scene.camera.shake_amount += 200
        self.app.sound_manager.play_sfx(self.app.ASSETS["sounds"]["enemy"]["boss"]["scream"])
        for _ in range(5):
            AnimatedParticle(
                self.app.ASSETS["animations"]["vfxs"]["darkness_big"],
                pg.Vector2(self.rect.center) + pg.Vector2(random.randint(-15, 15), random.randint(-15, 15))
            )
        pc = self.scene.player_status.player_character
        self.player_light = Light(400, pg.Vector2(pc.rect.center))

    def phase_3_start(self):
        """
        페이즈 3 시작 시 처리할 로직.
        모든 Soul 객체를 제거하고, 화면을 흔들고, 효과음과 파티클 효과를 재생.
        새로운 SpawnPattern을 등록.
        """
        souls = self.scene.get_objects_by_types(Soul)
        for soul in souls[:]:
            soul.destroy()
        self.scene.camera.shake_amount += 200
        self.app.sound_manager.play_sfx(self.app.ASSETS["sounds"]["enemy"]["boss"]["scream"])
        for _ in range(5):
            AnimatedParticle(
                self.app.ASSETS["animations"]["vfxs"]["darkness_big"],
                pg.Vector2(self.rect.center) + pg.Vector2(random.randint(-15, 15), random.randint(-15, 15))
            )
        self.registered_patterns["spawn"] = SpawnPattern(self)

    def phase_1_update(self):
        """
        페이즈 1 동안 매 프레임마다 실행될 업데이트 로직.
        """
        pass

    def phase_2_update(self):
        """
        페이즈 2 동안 매 프레임마다 실행될 업데이트 로직.
        플레이어 캐릭터의 위치에 따라 라이트 위치를 업데이트.
        """
        pc = self.scene.player_status.player_character
        self.player_light.position = pg.Vector2(pc.rect.center)

    def phase_3_update(self):
        """
        페이즈 3 동안 매 프레임마다 실행될 업데이트 로직.
        플레이어 캐릭터의 위치에 따라 라이트 위치를 업데이트.
        """
        pc = self.scene.player_status.player_character
        self.player_light.position = pg.Vector2(pc.rect.center)

    def phase_update(self):
        """
        현재 페이즈에 해당하는 업데이트 핸들러 메서드를 호출.
        """
        phase_name = self.PHASES[self.current_phase_index]["name"]
        update_handler = self.phase_update_handlers.get(phase_name)
        if update_handler:
            update_handler()

    def update(self):
        """
        몬스터의 상태를 매 프레임 업데이트.
        AI, 페이즈, 패턴, 애니메이션을 업데이트.
        """
        super().update()
        self.ai.update()
        self.check_phase()
        self.phase_update()
        self.update_patterns()
        self.control_animation()

    def destroy(self):
        super().destroy()
        self.app.change_scene("good_ending_cut_scene")

    def update_patterns(self):
        """
        등록된 모든 패턴을 업데이트.
        활성화된 패턴은 on_enabled_update를, 비활성화된 패턴은 on_disabled_update를 호출.
        """
        patterns = list(self.registered_patterns.values())
        for pattern in patterns:
            if pattern.enabled:
                pattern.on_enabled_update()
            else:
                pattern.on_disabled_update()

    def control_animation(self):
        """
        패턴 상태에 따라 몬스터의 애니메이션을 제어.
        """
        wander = self.registered_patterns["wander"]
        if wander.enabled:
            if wander.is_moving:
                self.set_action("run")
            else:
                self.set_action("idle")
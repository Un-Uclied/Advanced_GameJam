import pygame as pg
from collections import deque

from scripts.core import *
from scripts.constants import *
from scripts.vfx import *
from scripts.ui import *
from scripts.volume import *

MAX_HEALTH = 100
HURT_INVINCIBLE_TIME = 1
HEALTH_RESTORE_INTERVAL = 1.0
HEALTH_RESTORE_AMOUNT = 1
ATTACK_COOLTIME = 0.65

class PlayerAbilities:
    """
    플레이어 능력치 & 상태별 효과 관리 클래스

    - 대미지 처리, 체력 회복, 영혼 상호작용 담당
    - player_status에 붙어서 동작 (player_character는 외부에서 연결해야 함)
    """
    def __init__(self, status):
        self.status = status
        self.app = status.app
        self.player_character = None

        # 영혼 상호작용 이벤트 연결
        self.app.scene.event_bus.connect("on_soul_interact", self.on_soul_interact)
        self.app.scene.event_bus.connect("on_player_soul_changed", self._update_stats_by_soul_type)

        # 사운드 & 파티클 준비
        self.hurt_sound = self.app.ASSETS["sounds"]["player"]["hurt"]
        self.hurt_particle_anim = self.app.ASSETS["animations"]["vfxs"]["hurt"]

    def on_damage(self, damage: int):
        """피격 시 호출 - 무적 시작, 카메라 흔들림, 효과음 재생, 파티클 생성"""
        if self.status.current_invincible_time > 0:
            return  # 무적이면 무시
        
        self.status.current_invincible_time += HURT_INVINCIBLE_TIME

        self.app.scene.camera.shake_amount += damage * 2
        self.app.sound_manager.play_sfx(self.hurt_sound)

        if self.player_character:
            AnimatedParticle(self.hurt_particle_anim, pg.Vector2(self.player_character.rect.center))

    def on_soul_interact(self, soul_type: str):
        """영혼과 상호작용 처리"""
        if soul_type in self.status.soul_queue and soul_type != SOUL_DEFAULT:
            PopupText(f"\"{soul_type}는 이미 있다.\"", pg.Vector2(SCREEN_SIZE.x / 2, 700))
            return

        self.status.soul_queue.append(soul_type)
        self.app.scene.event_bus.emit("on_player_soul_changed")

    def _update_stats_by_soul_type(self):
        """영혼 상태에 따른 능력치 업데이트"""
        max_health = MAX_HEALTH
        if SOUL_KIND_C in self.status.soul_queue:
            max_health -= KIND_C_MAX_HEALTH_DOWN
        if SOUL_EVIL_B in self.status.soul_queue:
            max_health -= EVIL_B_MAX_HEALTH_DOWN

        self.status.max_health = max_health
        # 체력 현재값이 max_health보다 크면 자동 조절
        self.status.health = min(self.status.health, self.status.max_health)

        attack_cooltime = ATTACK_COOLTIME
        if SOUL_EVIL_A in self.status.soul_queue:
            attack_cooltime += EVIL_A_COOLTIME_UP
        if SOUL_EVIL_B in self.status.soul_queue:
            attack_cooltime -= EVIL_B_COOLTIME_DOWN

        self.status.attack_cooltime.max_time = attack_cooltime
        self.status.attack_cooltime.reset()

    def restore_health(self):
        """주기적으로 체력 회복 처리"""
        if 0 < self.status.health < self.status.max_health:
            heal_amount = HEALTH_RESTORE_AMOUNT

            # Kind A 영혼 보유 시 빛 안에서 추가 회복
            if SOUL_KIND_A in self.status.soul_queue and self.player_character:
                if Light.is_rect_in_light(self.app.scene.camera, self.player_character.rect):
                    heal_amount += KIND_A_HEALTH_UP

            self.status.health += heal_amount
            self.status.heal_timer.reset()

class PlayerStatus(GameObject):
    """
    플레이어 상태 관리 클래스
    - 체력, 무적 상태, 영혼 큐 관리
    - 관련 타이머 포함 (무적, 회복, 공격 쿨타임)
    - player_character는 외부에서 반드시 연결해야 함
    """
    def __init__(self, start_health: int):
        super().__init__()

        self._health = start_health
        self.max_health = MAX_HEALTH

        self.soul_queue = deque([SOUL_DEFAULT, SOUL_DEFAULT], maxlen=2)

        # PlayerAbilities 인스턴스 생성 & 연결
        self.abilities = PlayerAbilities(self)

        # 회복 타이머 (자동 체력 회복)
        self.heal_timer = Timer(
            time=HEALTH_RESTORE_INTERVAL,
            on_time_out=self.abilities.restore_health,
            auto_destroy=False,
        )
        self.heal_timer.active = True

        # 무적 시간
        self._current_invincible_time = 0

        # 공격 쿨타임 타이머
        self.attack_cooltime = Timer(
            time=ATTACK_COOLTIME,
            on_time_out=None,
            auto_destroy=False,
        )
        self.attack_cooltime.current_time = 0

        self.player_character = None  # 외부에서 연결 필수

    @property
    def health(self):
        return self._health

    @health.setter
    def health(self, value):
        scene = self.app.scene
        prev_health = self._health

        # 체력 범위 제한
        self._health = max(0, min(value, self.max_health))

        if self._health < prev_health:
            if self.current_invincible_time > 0:
                self._health = prev_health  # 무적 상태면 대미지 무시
                return

            scene.event_bus.emit("on_player_health_changed", False)
            self.abilities.on_damage(prev_health - self._health)

        else:
            scene.event_bus.emit("on_player_health_changed", True)

        if self._health <= 0:
            scene.event_bus.emit("on_player_died")

    @property
    def current_invincible_time(self):
        return self._current_invincible_time
    
    @current_invincible_time.setter
    def current_invincible_time(self, value):
        prev = self._current_invincible_time
        self._current_invincible_time = max(value, 0)

        if self._current_invincible_time > 0 and prev <= 0:
            self.app.scene.event_bus.emit("on_player_invincible", True)
        elif self._current_invincible_time <= 0 and prev > 0:
            self.app.scene.event_bus.emit("on_player_invincible", False)

    def update(self):
        self.current_invincible_time -= self.app.dt
from collections import deque
import pygame as pg

from scripts.core import GameObject, Timer
from scripts.constants import *
from scripts.vfx import AnimatedParticle
from scripts.ui import PopupText

MAX_HEALTH = 100
HURT_INVINCIBLE_TIME = 1
HEALTH_RESTORE_INTERVAL = 1.0
HEALTH_RESTORE_AMOUNT = 1
ATTACK_COOLTIME = 0.65

class PlayerAbilities:
    """
    플레이어 능력치 & 상태별 효과 관리 클래스.
    
    `PlayerStatus` 객체의 상태를 기반으로 대미지 처리, 체력 회복, 영혼 상호작용 등
    플레이어의 실제 게임 로직을 담당함.
    `PlayerStatus`와 약하게 연결되어 이벤트를 통해 상태 변화를 감지하고 반응함.
    """
    def __init__(self, status: "PlayerStatus"):
        self.status = status
        self.app = status.app
        # player_character는 status에서 직접 참조함.
        
        # 영혼 상호작용 관련 이벤트 리스너 등록
        self.app.scene.event_bus.connect("on_soul_interact", self.on_soul_interact)
        
        # 능력치 업데이트 이벤트 리스너 등록
        self.app.scene.event_bus.connect("on_player_soul_changed", self.update_stats_by_soul_type)
        
        # 피격 이벤트 리스너 등록
        self.app.scene.event_bus.connect("on_player_damaged", self.on_player_damaged)
        
        # 사운드 & 파티클 준비
        self.hurt_sound = self.app.ASSETS["sounds"]["player"]["hurt"]
        self.hurt_particle_anim = self.app.ASSETS["animations"]["vfxs"]["hurt"]

        # 체력 회복 타이머를 생성함.
        self.heal_timer = Timer(
            time=HEALTH_RESTORE_INTERVAL,
            on_time_out=self.restore_health_tick,
            auto_destroy=False,
            use_unscaled=False
        )
        self.heal_timer.active = True

    def on_player_damaged(self, damage: int):
        """플레이어가 대미지를 입었을 때 호출되는 콜백."""
        self.status.current_invincible_time += HURT_INVINCIBLE_TIME
        
        # 이벤트 버스를 통해 카메라, 사운드, 파티클 처리를 분리함.
        # 이렇게 하면 `PlayerAbilities`가 직접적으로 다른 객체에 의존하지 않게 됨.
        self.app.scene.event_bus.emit("on_camera_shake", damage * 2)
        self.app.sound_manager.play_sfx(self.hurt_sound)
        
        if self.status.player_character:
            AnimatedParticle(self.hurt_particle_anim, pg.Vector2(self.status.player_character.rect.center))

    def on_soul_interact(self, soul_type: str):
        """영혼과 상호작용 처리."""
        if soul_type in self.status.soul_queue and soul_type != SOUL_DEFAULT:
            PopupText(f"\"{soul_type}는 이미 있다.\"", pg.Vector2(SCREEN_SIZE.x / 2, 700))
            return

        self.status.soul_queue.append(soul_type)
        self.app.scene.event_bus.emit("on_player_soul_changed")

    def update_stats_by_soul_type(self):
        """영혼 상태에 따른 능력치 업데이트."""
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

    def restore_health_tick(self):
        """
        주기적으로 체력 회복을 처리하는 콜백 함수.
        타이머에 의해 호출됨.
        """
        self.heal_timer.reset()
        if 0 < self.status.health < self.status.max_health:
            heal_amount = HEALTH_RESTORE_AMOUNT

            # Kind A 영혼 보유 시 빛 안에서 추가 회복
            if SOUL_KIND_A in self.status.soul_queue and self.status.player_character:
                # `LightManager`를 사용해 충돌 검사
                if self.app.scene.light_manager.is_rect_in_light(self.status.player_character.rect):
                    heal_amount += KIND_A_HEALTH_UP
            
            # `PlayerStatus`의 `health` setter를 통해 체력 회복
            self.status.health += heal_amount

class PlayerStatus(GameObject):
    """
    플레이어 상태 관리 클래스.
    
    체력, 무적 상태, 영혼 큐 등 순수한 상태 데이터만 관리하고,
    상태 변화 시 이벤트를 발생시키는 역할을 함.
    """
    def __init__(self, start_health: int):
        super().__init__()

        self._health = start_health
        self.max_health = MAX_HEALTH

        self.soul_queue = deque([SOUL_DEFAULT, SOUL_DEFAULT], maxlen=2)

        # PlayerAbilities 인스턴스 생성 및 연결
        self.abilities = PlayerAbilities(self)
        
        # 무적 시간
        self._current_invincible_time = 0

        # 공격 쿨타임 타이머
        self.attack_cooltime = Timer(
            time=ATTACK_COOLTIME,
            on_time_out=None,
            auto_destroy=False,
        )
        self.attack_cooltime.active = True # 타이머가 동작하도록 활성화

        self.player_character = None

    @property
    def health(self) -> float:
        return self._health

    @health.setter
    def health(self, value: float):
        prev_health = self._health
        
        # 체력 범위 제한
        self._health = max(0, min(value, self.max_health))

        # 대미지 처리 로직
        if self._health < prev_health:
            # 무적 상태면 대미지 무시하고 복구
            if self.current_invincible_time > 0:
                self._health = prev_health
                return
            
            damage_amount = prev_health - self._health
            self.app.scene.event_bus.emit("on_player_health_changed", False)
            # 대미지 처리 로직을 `PlayerAbilities`로 옮기고 이벤트로 호출
            self.app.scene.event_bus.emit("on_player_damaged", damage_amount)
            
        # 회복 처리 로직
        elif self._health > prev_health:
            self.app.scene.event_bus.emit("on_player_health_changed", True)

        # 사망 처리
        if self._health <= 0:
            self.app.scene.event_bus.emit("on_player_died")

    @property
    def current_invincible_time(self) -> float:
        return self._current_invincible_time
    
    @current_invincible_time.setter
    def current_invincible_time(self, value: float):
        prev = self._current_invincible_time
        self._current_invincible_time = max(value, 0)

        # 무적 상태 변화 시 이벤트 발생
        if self._current_invincible_time > 0 and prev <= 0:
            self.app.scene.event_bus.emit("on_player_invincible", True)
        elif self._current_invincible_time <= 0 and prev > 0:
            self.app.scene.event_bus.emit("on_player_invincible", False)

    def update(self):
        # `Timer` 객체들이 `GameObject`이므로 `GameObject.update_all()`을 통해
        # 자동으로 업데이트됨. 따라서 여기서 별도로 호출할 필요 없음.
        self.current_invincible_time -= self.app.dt
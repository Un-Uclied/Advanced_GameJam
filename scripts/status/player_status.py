import pygame as pg
from collections import deque

from scripts.core import *
from scripts.constants import *
from scripts.vfx import *
from scripts.ui import *
from scripts.volume import *

MAX_HEALTH = 100
INVINCIBLE_DURATION = 1.5
HEALTH_RESTORE_INTERVAL = 1.0
HEALTH_RESTORE_AMOUNT = 1

ATTACK_COOLTIME = .65

class PlayerAbilities:
    """
    플레이어의 특수 능력 및 상태에 따른 효과를 관리합니다.
    대미지 처리, 체력 회복, 영혼 상호작용 로직을 담당합니다.
    """
    def __init__(self, status):
        self.status = status
        self.app = status.app
        self.player_character = None
        
        # 영혼과 인터랙트 했을 때 이벤트 연결
        self.app.scene.event_bus.connect("on_soul_interact", self.on_soul_interact)
        
        self.hurt_sound = self.app.ASSETS["sounds"]["player"]["hurt"]
        self.hurt_particle_anim = self.app.ASSETS["animations"]["vfxs"]["hurt"]

    def on_damage(self, damage: int):
        """플레이어가 대미지를 입었을 때 처리"""
        self.status.is_invincible = True
        self.status.invincible_timer.active = True
        self.status.invincible_timer.reset()
        
        scene = self.app.scene
        scene.event_bus.emit("on_player_invincible", True)
        
        cam = scene.camera
        cam.shake_amount += damage * 2
        self.app.sound_manager.play_sfx(self.hurt_sound)
        
        if self.player_character:
            AnimatedParticle(
                self.hurt_particle_anim,
                pg.Vector2(self.player_character.rect.center)
            )

    def on_soul_interact(self, soul_type: str):
        """영혼과 상호작용 했을 때 처리"""
        if soul_type in self.status.soul_queue and not soul_type == SOUL_DEFAULT:
            PopupText(f"\"{soul_type}는 이미 있다.\"", pg.Vector2(SCREEN_SIZE.x / 2, 700))
            return
        
        self.status.soul_queue.append(soul_type)
        self.app.scene.event_bus.emit("on_player_soul_changed")
        
        self._update_stats_by_soul_type()

    def _update_stats_by_soul_type(self):
        """영혼 타입에 따라 플레이어 능력치 업데이트"""
        max_health = MAX_HEALTH
        if SOUL_KIND_C in self.status.soul_queue:
            max_health -= KIND_C_MAX_HEALTH_DOWN
        if SOUL_EVIL_B in self.status.soul_queue:
            max_health -= EVIL_B_MAX_HEALTH_DOWN
        self.status.max_health = max_health
        self.status.health = self.status.health
        
        attack_cooltime = ATTACK_COOLTIME
        if SOUL_EVIL_A in self.status.soul_queue:
            attack_cooltime += EVIL_A_COOLTIME_UP
        if SOUL_EVIL_B in self.status.soul_queue:
            attack_cooltime -= EVIL_B_COOLTIME_DOWN
        self.status.attack_cooltime.max_time = attack_cooltime
        self.status.attack_cooltime.reset()

    def restore_health(self):
        """일정 간격으로 체력 회복"""
        if 0 < self.status.health < self.status.max_health:
            self.status.health += HEALTH_RESTORE_AMOUNT
            
            if SOUL_KIND_A in self.status.soul_queue and self.player_character and Light.is_rect_in_light(self.app.scene.camera, self.player_character.rect):
                self.status.health += KIND_A_HEALTH_UP
            
            self.status.heal_timer.reset()

class PlayerStatus(GameObject):
    """
    플레이어의 상태(체력, 무적, 영혼 큐)를 관리하는 핵심 클래스
    """
    def __init__(self, start_health: int):
        super().__init__()
        
        self._health = start_health
        self.max_health = MAX_HEALTH
        self.is_invincible = False
        
        self.soul_queue = deque([SOUL_DEFAULT, SOUL_DEFAULT], maxlen=2)
        
        # PlayerAbilities 인스턴스 생성 및 연결
        self.abilities = PlayerAbilities(self)
        
        # 타이머
        self.heal_timer = Timer(
            time=HEALTH_RESTORE_INTERVAL,
            on_time_out=self.abilities.restore_health,
            auto_destroy=False
        )
        self.heal_timer.active = True
        
        self.invincible_timer = Timer(
            time=INVINCIBLE_DURATION,
            on_time_out=self.end_invincibility,
            auto_destroy=False
        )
        self.invincible_timer.active = False
        
        self.attack_cooltime = Timer(
            time=ATTACK_COOLTIME,
            on_time_out=None,
            auto_destroy=False
        )
        self.attack_cooltime.current_time = 0

    def end_invincibility(self):
        """무적 상태 종료"""
        self.is_invincible = False
        self.app.scene.event_bus.emit("on_player_invincible", False)

    @property
    def health(self):
        return self._health

    @health.setter
    def health(self, value):
        prev = self._health
        self._health = max(min(value, self.max_health), 0)
        
        if self._health < prev:
            if self.is_invincible:
                self._health = prev
                return
            self.abilities.on_damage(prev - self._health)
        
        scene = self.app.scene
        if self._health <= 0:
            scene.event_bus.emit("on_player_died")
        scene.event_bus.emit("on_player_health_changed")

    def update(self):
        Light.is_rect_in_light(self.app.scene.camera, self.player_character.rect)
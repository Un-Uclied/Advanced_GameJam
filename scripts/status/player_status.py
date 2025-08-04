import pygame as pg
from collections import deque # 큐!!

from scripts.core import *
from scripts.constants import *
from scripts.vfx import *

MAX_HEALTH = 100
INVINCIBLE_DURATION = 1.5
HEALTH_RESTORE_INTERVAL = 1.0
HEALTH_RESTORE_AMOUNT = 1

class PlayerStatus(GameObject):
    def __init__(self, start_health : int):
        super().__init__()

        self._health = start_health
        self.is_invincible = False

        # 영혼 큐 | 최대 길이는 2이고, 새로운걸 밀어 넣으면 가장 오래된건 없어짐.
        self.soul_queue = deque([SOUL_DEFAULT, SOUL_DEFAULT], maxlen=2)
        self.player_character = None # 얘는 밖에서 달아줘야함!!

        # 체력 회복용 타이머 (얘는 항상 힐 하려고 함)
        self.heal_timer = Timer(
            time=HEALTH_RESTORE_INTERVAL,
            on_time_out=self.restore_health,
            auto_destroy=False
        )
        self.heal_timer.active = True

        # 무적 타이머
        self.invincible_timer = Timer(
            time=INVINCIBLE_DURATION,
            on_time_out=self.end_invincibility,
            auto_destroy=False
        )
        self.invincible_timer.active = False

        # 영혼과 인터랙트 했을때 on_soul_interact이 불리고, 타입이 인수로 들어오고 soul_queue에 그 타입을 밀어넣음.
        self.app.scene.event_bus.on("on_soul_interact", self.on_soul_interact)

        self.hurt_sound = self.app.ASSETS["sounds"]["player"]["hurt"]
        self.hurt_particle_anim = self.app.ASSETS["animations"]["vfxs"]["hurt"]

    @property
    def health(self):
        '''간단한 체력 시스템 (on_player_health_changed 이벤트 있음)'''
        return self._health

    @health.setter
    def health(self, value):
        '''이떄 on_player_health_changed emit됨'''
        # 바뀌기전 체력 저장 | 체력 clamp
        prev = self._health
        self._health = max(min(value, MAX_HEALTH), 0)

        # 체력이 깎였다면 깎인량을 on_damage에 건네줌
        if self._health < prev:
            # 무적 상태인데 체력이 깎였다면 원상복구후 리턴
            if self.is_invincible:
                self._health = prev
                return

            self.on_damage(prev - self._health)

        # 체력이 0이되면 해당 레벨을 다시 시작
        if self._health <= 0:
            self.app.change_scene("main_game_scene")

        # 체력 바뀐 이벤트 emit
        scene = self.app.scene
        scene.event_bus.emit("on_player_health_changed")

    def on_soul_interact(self, soul_type : str):
        self.soul_queue.append(soul_type)
        self.app.scene.event_bus.emit("on_player_soul_changed")

    def on_damage(self, damage: int):
        # 무적 타이머 시작
        self.is_invincible = True
        self.invincible_timer.active = True
        self.invincible_timer.reset()
        
        # on_player_invincible_start emit하기
        scene = self.app.scene
        scene.event_bus.emit("on_player_invincible_start")

        # 이펙트
        cam = scene.camera
        cam.shake_amount += damage * 2
        self.app.sound_manager.play_sfx(self.hurt_sound)

        # 파티클
        AnimatedParticle(
            self.hurt_particle_anim,
            pg.Vector2(self.player_character.rect.center)
        )

    def end_invincibility(self):
        # 끝
        self.is_invincible = False
        scene = self.app.scene

        # on_player_invincible_end emit하기
        scene.event_bus.emit("on_player_invincible_end")

    def restore_health(self):
        # 계속 인터벌 마다 불림.
        if 0 < self._health < MAX_HEALTH:
            self.health += HEALTH_RESTORE_AMOUNT
            self.heal_timer.reset()
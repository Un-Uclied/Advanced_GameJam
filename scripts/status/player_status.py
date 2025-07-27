import pygame as pg

from scripts.vfx import *

class PlayerStatus:
    '''씬 시작시 PlayerStatus를 생성, 레벨 생성시 인스턴스.player_character = 엔티티 인스턴스 걸어줘야함. (살짝 위험한 구조)'''
    def __init__(self, scene):
        self.scene = scene
        self.camera = self.scene.camera

        self.max_health = 100
        self._health = self.max_health

        self.is_invincible = False
        self.max_invincible_timer = 1.5
        self.current_invincible_timer = 0

    @property
    def health(self):
        return self._health
    
    @health.setter
    def health(self, value):
        if self.is_invincible: return

        before_health = self._health
        self._health = max(min(value, self.max_health), 0)

        #체력이 깎였을때
        if before_health > self._health:
            self.is_invincible = True
            self.camera.shake_amount += (before_health - self._health) * 2
            self.current_invincible_timer = self.max_invincible_timer

            #맞는 소리 재생, 맞는 파티클 생성
            self.scene.app.ASSETS["sounds"]["player"]["hurt"].play()
            AnimatedParticle("hurt", pg.Vector2(self.player_character.rect.center))

        #플레이어 캐릭터 제거
        if self._health <= 0:
            self.player_character.destroy()
            self.player_character = None

    def on_update(self):
        dt = self.scene.app.dt
        if self.current_invincible_timer > 0:
            self.current_invincible_timer -= dt
            self.is_invincible = True
        else:
            self.is_invincible = False
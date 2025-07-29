import pygame as pg

from scripts.vfx import *

MAX_INVINCIBLE_TIME = 1.5
MAX_HEALTH = 100

class PlayerStatus:
    '''
    씬 시작시 PlayerStatus를 생성, 레벨 생성시 인스턴스.player_character = 엔티티 인스턴스 걸어줘야함. (살짝 위험한 구조)
    
    :param scene: 무.조.건. MainGameScene의 인스턴스!!!
    '''

    def __init__(self, scene):
        self.scene = scene

        self._health = MAX_HEALTH

        self.is_invincible = False
        self.current_invincible_timer = 0

        #MainGameScene에서 on_death_event.append(메소드)이렇게 하면 플레이어가 죽을때 그 메소드가 불림.
        self.on_death_event = []
    
    def on_dead(self):
        for event in self.on_death_event:
            event(self)

    @property
    def health(self):
        return self._health
    
    @health.setter
    def health(self, value):
        #무적 상태라면 리턴
        if self.is_invincible: return

        #깎이기 전 체력 저장
        before_health = self._health
        self._health = max(min(value, MAX_HEALTH), 0) #0~100 넘기지 않게

        #체력이 깎였을때
        if before_health > self._health:
            self.current_invincible_timer = MAX_INVINCIBLE_TIME              #무적 시간을 늘리면 무적 상태가 됨.
            self.scene.camera.shake_amount += (before_health - self._health) * 2   #받은 대미지의 두배만큼 카메라 흔들기

            #맞는 소리 재생, 맞는 파티클 생성
            self.scene.app.sound_manager.play_sfx(self.scene.app.ASSETS["sounds"]["player"]["hurt"])
            AnimatedParticle("hurt", pg.Vector2(self.player_character.rect.center))

        if self.health <= 0:
            self.on_dead()
            self.player_character.destroy()

            # 이렇게 하면 아무도 참조 안해서 GC가 가져감
            self.player_character = None

    def update(self):
        dt = self.scene.app.dt
        if self.current_invincible_timer > 0:
            self.current_invincible_timer -= dt
            self.is_invincible = True
        else:
            self.is_invincible = False
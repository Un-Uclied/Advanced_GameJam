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

        app = self.scene.app
        self.hurt_sound = app.ASSETS["sounds"]["player"]["hurt"]
        self.hurt_particle_anim = app.ASSETS["animations"]["vfxs"]["hurt"]

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
        app = self.scene.app
        camera = self.scene.camera
        if before_health > self._health:
            self.current_invincible_timer = MAX_INVINCIBLE_TIME              #무적 시간을 늘리면 무적 상태가 됨.
            camera.shake_amount += (before_health - self._health) * 2   #받은 대미지의 두배만큼 카메라 흔들기

            #맞는 소리 재생, 맞는 파티클 생성
            app.sound_manager.play_sfx(self.hurt_sound)
            AnimatedParticle(self.hurt_particle_anim, pg.Vector2(self.player_character.rect.center))

        if self.health <= 0:
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
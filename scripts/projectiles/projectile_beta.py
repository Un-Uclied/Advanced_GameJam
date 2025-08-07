import pygame as pg

from scripts.vfx import *
from scripts.core import *
from .base import Projectile

DEFAULT_LIFE_TIME = 5

class ProjectileBeta(Projectile):
    '''
    TwoBeta의 탄환!!
    
    :param start_position: 시작 위치!! (대개로 pg.Vector2(엔티티.rect.center))
    :param start_direction: 탄환 방향!!
    '''
    
    def __init__(self, start_position : pg.Vector2, start_direction : pg.Vector2):
        super().__init__("two_beta_projectile",
                         start_position,
                         start_direction)
        
        Timer(DEFAULT_LIFE_TIME, lambda: self.destroy())

        # TwoBeta 클래스의 적 탄환 생성 소리 재생
        self.app.sound_manager.play_sfx(self.app.ASSETS["sounds"]["enemy"]["projectile"])

        self.destroy_particle_anim = self.app.ASSETS["animations"]["vfxs"]["projectile_destroy"]["player"]

    def destroy(self):
        # TwoBeta 클래스의 적 탄환 제거 파티클 생성
        AnimatedParticle(self.destroy_particle_anim, self.position)
        super().destroy()
        
    def update(self):
        super().update()

        #현재씬의 플레이어 스테이터스에 접근, 플레이어 스테이터스의 플레이어 캐릭터에 접근
        #탄환이 닿으면 플레이어 스테이터스의 체력을 깎고 자기 자신 제거
        ps = self.app.scene.player_status
        pc = ps.player_character
        if pc.rect.collidepoint(self.position):
            ps.health -= self.data["damage"]
            self.destroy()
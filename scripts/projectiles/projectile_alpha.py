import pygame as pg

from scripts.vfx import AnimatedParticle

from .base import Projectile
class ProjectileAlpha(Projectile):
    '''
    OneBeta의 탄환!!
    
    :param start_position: 시작 위치!! (대개로 pg.Vector2(엔티티.rect.center))
    :param start_direction: 탄환 방향!!
    '''

    def __init__(self, start_position : pg.Vector2, start_direction : pg.Vector2):
        super().__init__("two_alpha_projectile",
                         start_position,
                         start_direction)
        
        # TwoAlpha 클래스의 적 탄환 생성 소리 재생
        self.app.sound_manager.play_sfx(self.app.ASSETS["sounds"]["enemy"]["projectile"])
    
    def destroy(self):
        # TwoAlpha 클래스의 적 탄환 제거 파티클 생성
        AnimatedParticle("enemy_alpha_projectile_destroy", self.position)
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
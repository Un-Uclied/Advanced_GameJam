import pygame as pg

from scripts.core import *
from scripts.constants import *
from scripts.vfx import AnimatedParticle
from .base import Projectile

DEFAULT_LIFE_TIME = 4

class PlayerProjectile(Projectile):
    '''
    플레이어의 탄환!!
    
    :param start_position: 시작 위치!! (대개로 pg.Vector2(엔티티.rect.center))
    :param start_direction: 탄환 방향!!
    '''
    def __init__(self, start_position : pg.Vector2, start_direction : pg.Vector2):
        super().__init__("player_projectile",
                         start_position,
                         start_direction)
        
        self.attacked_enemies = []

        # 일정 시간후에 삭제
        life_time = DEFAULT_LIFE_TIME
        ps = self.app.scene.player_status
        if SOUL_EVIL_A in ps.soul_queue:
            life_time -= EVIL_A_LIFE_TIME_DOWN 
        Timer(life_time, lambda: self.destroy())

        # 플레이어 탄환 생성 소리 재생
        self.app.sound_manager.play_sfx(self.app.ASSETS["sounds"]["player"]["projectile"])

        self.destroy_particle_anim = self.app.ASSETS["animations"]["vfxs"]["projectile_destroy"]["player"]

    def destroy(self):
        # 플레이어 탄환 제거 파티클 생성
        AnimatedParticle(self.destroy_particle_anim, self.position)
        super().destroy()
    
    def update_tilemap_collision(self):
        '''SOUL_EVIL_A를 장착중이면 타일맵에 충돌됐을때도 부숴지지 않음'''
        ps = self.app.scene.player_status
        if SOUL_EVIL_A in ps.soul_queue:
            return
        else:
            super().update_tilemap_collision()

    def update(self):
        super().update()
        ps = self.app.scene.player_status
        pc = ps.player_character

        # SOUL_EVIL_A를 장착하고 있다면 그만큼 추가적으로 많이 움직이기
        if SOUL_EVIL_A in ps.soul_queue:
            self.position += self.direction * EVIL_A_PROJECTILE_SPEED_UP * self.app.dt

        from scripts.enemies import ALL_ENEMY_TYPE # 순환 참조 피하기;;
        # 생성된 적 반복문 돌아서 닿으면 대미지 주고 자기자신 제거
        all_enemies = GameObject.get_objects_by_types(ALL_ENEMY_TYPE)
        for enemy in all_enemies:
            if enemy.rect.collidepoint(self.position):
                # 한 탄환이 한 적을 여러번 공격 못하게
                if enemy in self.attacked_enemies:
                    continue
                self.attacked_enemies.append(enemy)

                damage = self.data["damage"]
                # 영혼 타입에 맞춰서 대미지 바꾸기
                if SOUL_KIND_B in ps.soul_queue:
                    damage -= KIND_B_ATTACK_DAMAGE_DOWN
                
                # 적 대미지 깎기
                enemy.status.health -= damage

                # SOUL_EVIL_A를 장착하고 있다면 적을 맞혀도 사라지지 않음
                if not SOUL_EVIL_A in ps.soul_queue:
                    self.destroy()
                    break
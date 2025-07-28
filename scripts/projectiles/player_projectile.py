import pygame as pg

from scripts.objects import GameObject
from scripts.vfx import AnimatedParticle

from .base import Projectile
class PlayerProjectile(Projectile):
    def __init__(self, start_position : pg.Vector2, start_direction : pg.Vector2):
        super().__init__("player_projectile",
                         start_position,
                         start_direction)
        
        # 플레이어 탄환 생성 소리 재생
        self.app.ASSETS["sounds"]["player"]["projectile"].play()

    def destroy(self):
        # 플레이어 탄환 제거 파티클 생성
        AnimatedParticle("player_projectile_destroy", self.position)
        super().destroy()
        
    def update(self):
        super().update()
        
        
        from scripts.enemies import ALL_ENEMY_TYPE # 순환 참조 피하기;;
        # 생성된 적 반복문 돌아서 닿으면 대미지 주고 자기자신 제거
        all_enemies = GameObject.get_objects_by_types(ALL_ENEMY_TYPE)
        for enemy in all_enemies:
            if enemy.rect.collidepoint(self.position):
                enemy.status.health -= self.data["damage"]
                self.destroy()
                break
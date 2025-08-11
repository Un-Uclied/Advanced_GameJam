import pygame as pg

from scripts.vfx import *
from scripts.core import *
from .base import EnemyProjectile

DEFAULT_LIFE_TIME = 5

class ProjectileBeta(EnemyProjectile):
    """
    TwoBeta 적 탄환 클래스

    Args:
        start_position (pg.Vector2): 탄환 시작 위치 (보통 적 캐릭터 위치)
        start_direction (pg.Vector2): 탄환 이동 방향 벡터
    """

    def __init__(self, start_position: pg.Vector2, start_direction: pg.Vector2):
        super().__init__("two_beta_projectile", start_position, start_direction, DEFAULT_LIFE_TIME, destroy_on_tilemap_collision=False)

        # 발사 시 효과음 재생
        self.app.sound_manager.play_sfx(self.app.ASSETS["sounds"]["enemy"]["projectile"])

        # 파괴 시 재생할 파티클 애니메이션 지정
        self.destroy_particle_anim = self.app.ASSETS["animations"]["vfxs"]["projectile_destroy"]["enemy_beta"]

    def destroy(self):
        """
        파괴 처리: 파티클 생성, 부모 파괴 호출
        """
        AnimatedParticle(self.destroy_particle_anim, self.position)
        super().destroy()
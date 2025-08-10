import pygame as pg

from scripts.vfx import *
from scripts.core import *
from .base import Projectile

DEFAULT_LIFE_TIME = 3

class ProjectileAlpha(Projectile):
    """
    OneBeta 적 탄환 클래스
    
    Args:
        start_position (pg.Vector2): 탄환 시작 위치 (보통 적 탄환 스폰 위치)
        start_direction (pg.Vector2): 탄환 이동 방향 벡터
    """

    def __init__(self, start_position: pg.Vector2, start_direction: pg.Vector2):
        super().__init__("two_alpha_projectile", start_position, start_direction)

        # 기본 수명 타이머 설정, 수명 끝나면 자동 파괴
        self.timer = Timer(DEFAULT_LIFE_TIME, self.destroy)

        # 적 탄환 발사 시 사운드 재생
        self.app.sound_manager.play_sfx(self.app.ASSETS["sounds"]["enemy"]["projectile"])

        # 파괴 시 재생할 파티클 애니메이션 지정
        self.destroy_particle_anim = self.app.ASSETS["animations"]["vfxs"]["projectile_destroy"]["enemy_alpha"]

    def destroy(self):
        """
        탄환 파괴 처리:
        타이머 종료, 파티클 생성, 부모 클래스 파괴 호출
        """
        self.timer.destroy()
        AnimatedParticle(self.destroy_particle_anim, self.position)
        super().destroy()

    def update(self):
        """
        매 프레임 업데이트:
        - 기본 이동, 애니메이션 갱신
        - 플레이어와 충돌 검사, 맞으면 플레이어 체력 감소 및 탄환 파괴
        """
        super().update()

        ps = self.app.scene.player_status
        pc = ps.player_character

        # 플레이어가 탄환 위치에 닿으면 대미지 주고 탄환 파괴
        if pc.rect.collidepoint(self.position):
            ps.health -= self.data["damage"]
            self.app.scene.event_bus.emit("on_player_hurt", self.data["damage"])
            self.destroy()
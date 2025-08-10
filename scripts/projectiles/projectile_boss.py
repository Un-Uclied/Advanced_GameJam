import pygame as pg

from scripts.vfx import *
from scripts.ui import *
from scripts.constants import *
from scripts.core import *
from .base import Projectile

DEFAULT_LIFE_TIME = 4

class ProjectileBoss(Projectile):
    """
    FiveOmega 적 탄환 클래스

    Args:
        start_position (pg.Vector2): 탄환 시작 위치 (보통 적 캐릭터 위치)
        start_direction (pg.Vector2): 탄환 이동 방향 벡터
    """

    def __init__(self, start_position: pg.Vector2, start_direction: pg.Vector2):
        super().__init__("boss_projectile", start_position, start_direction)

        # 탄환 수명 타이머 설정, 끝나면 자동 파괴
        self.timer = Timer(DEFAULT_LIFE_TIME, self.destroy)

        # 발사 시 효과음 재생
        self.app.sound_manager.play_sfx(self.app.ASSETS["sounds"]["enemy"]["projectile"])

        # 파괴 시 재생할 파티클 애니메이션 지정
        self.destroy_particle_anim = self.app.ASSETS["animations"]["vfxs"]["projectile_destroy"]["enemy_beta"]

    def destroy(self):
        """
        파괴 처리: 타이머 종료, 파티클 생성, 부모 파괴 호출
        """
        self.timer.destroy()
        AnimatedParticle(self.destroy_particle_anim, self.position)
        super().destroy()

    def update(self):
        """
        매 프레임:
        - 기본 이동/애니메이션 갱신
        - 플레이어와 충돌 검사, 맞으면 플레이어 체력 감소 및 탄환 파괴
        """
        super().update()

        ps = self.app.scene.player_status
        pc = ps.player_character

        if pc.rect.collidepoint(self.position):
            # 무적이 아니고, 큐가 비어있지 않고, 전부 DEFAULT가 아닐 때만 실행
            if ps.current_invincible_time <= 0 and ps.soul_queue and not all(soul == SOUL_DEFAULT for soul in ps.soul_queue):
                for i in range(len(ps.soul_queue)):
                    ps.soul_queue[i] = SOUL_DEFAULT  # 값 교체
                self.app.scene.event_bus.emit("on_player_soul_changed")
                PopupText(
                    "혼이 감염되어 소멸해버렸다...",
                    pg.Vector2(SCREEN_SIZE.x / 2, 680),
                    fade_delay=.25,
                    fade_duration=1.5
                )
            ps.health -= self.data["damage"]
            self.app.scene.event_bus.emit("on_player_hurt", self.data["damage"])
            self.destroy()
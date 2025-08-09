import pygame as pg

from scripts.core import *
from scripts.constants import *
from scripts.vfx import AnimatedParticle
from .base import Projectile

DEFAULT_LIFE_TIME = 4

class PlayerProjectile(Projectile):
    """
    플레이어가 쏘는 탄환 클래스

    Args:
        start_position (pg.Vector2): 탄환 시작 위치 (보통 플레이어 중심)
        start_direction (pg.Vector2): 탄환 이동 방향 벡터
    """
    def __init__(self, start_position: pg.Vector2, start_direction: pg.Vector2):
        super().__init__("player_projectile", start_position, start_direction)

        self.attacked_enemies = []  # 이미 공격한 적 리스트 (중복 공격 방지)

        # 탄환 수명 설정 (기본값에서 특정 영혼 효과에 따라 감소 가능)
        life_time = DEFAULT_LIFE_TIME
        ps = self.app.scene.player_status
        if SOUL_EVIL_A in ps.soul_queue:
            life_time -= EVIL_A_LIFE_TIME_DOWN
        
        self.timer = Timer(life_time, self.destroy)  # 수명 다하면 자동 파괴

        # 생성 사운드 재생
        self.app.sound_manager.play_sfx(self.app.ASSETS["sounds"]["player"]["projectile"])

        # 파괴 시 재생할 파티클 애니메이션
        self.destroy_particle_anim = self.app.ASSETS["animations"]["vfxs"]["projectile_destroy"]["player"]

    def destroy(self):
        """
        탄환 파괴 처리: 타이머 삭제, 파티클 생성, 부모 클래스 파괴 호출
        """
        self.timer.destroy()
        AnimatedParticle(self.destroy_particle_anim, self.position)
        super().destroy()

    def update_tilemap_collision(self):
        """
        SOUL_EVIL_A 영혼 장착 시 타일맵 충돌 무시,
        그렇지 않으면 기본 타일맵 충돌 처리 호출
        """
        ps = self.app.scene.player_status
        if SOUL_EVIL_A in ps.soul_queue:
            return
        super().update_tilemap_collision()

    def update(self):
        """
        매 프레임 업데이트:
        - 기본 이동 및 애니메이션 갱신
        - SOUL_EVIL_A 효과 시 속도 증가
        - 적과 충돌 검사, 대미지 처리 및 탄환 파괴
        """
        super().update()

        ps = self.app.scene.player_status

        # SOUL_EVIL_A 효과로 탄환 추가 이동
        if SOUL_EVIL_A in ps.soul_queue:
            self.position += self.direction * EVIL_A_PROJECTILE_SPEED_UP * self.app.dt

        from scripts.enemies import ALL_ENEMY_TYPE  # 순환 참조 회피용 임포트
        all_enemies = GameObject.get_objects_by_types(ALL_ENEMY_TYPE)

        for enemy in all_enemies:
            if enemy.rect.collidepoint(self.position):
                if enemy in self.attacked_enemies:
                    continue  # 이미 공격한 적은 패스

                self.attacked_enemies.append(enemy)
                damage = self.data["damage"]

                # SOUL_KIND_B 효과로 공격력 감소 적용
                if SOUL_KIND_B in ps.soul_queue:
                    damage -= KIND_B_ATTACK_DAMAGE_DOWN

                enemy.status.health -= damage

                # SOUL_EVIL_A 없으면 공격 후 파괴
                if SOUL_EVIL_A not in ps.soul_queue:
                    self.destroy()
                    break
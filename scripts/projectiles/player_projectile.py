import pygame as pg

from scripts.utils import *
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
        # super().__init__()부르기 전이라 어쩔수 없이 직접 임포트해서 싱글톤 접근
        from scripts.app import App
        app = App.singleton

        ps = app.scene.player_status
        # 기본 수명 세팅, SOUL_EVIL_A 있으면 수명 줄임
        life_time = DEFAULT_LIFE_TIME
        if SOUL_EVIL_A in ps.soul_queue:
            life_time -= EVIL_A_LIFE_TIME_DOWN
        
        # SOUL_EVIL_A 있으면 벽 충돌시 파괴 안되게 설정
        destroy_on_tilemap_collision = not (SOUL_EVIL_A in ps.soul_queue)
        
        super().__init__(
            "player_projectile",
            start_position,
            start_direction,
            life_time,
            destroy_on_tilemap_collision=destroy_on_tilemap_collision
        )

        self.attacked_enemies = []  # 이미 공격한 적 리스트 (중복 공격 방지)

        # 생성 사운드 재생
        self.app.sound_manager.play_sfx(self.app.ASSETS["sounds"]["player"]["projectile"])

        # 파괴 시 재생할 파티클 애니메이션
        self.destroy_particle_anim = self.app.ASSETS["animations"]["vfxs"]["projectile_destroy"]["player"]

    def destroy(self):
        """
        탄환 파괴 처리: 타이머 삭제, 파티클 생성, 부모 클래스 파괴 호출
        """
        AnimatedParticle(self.destroy_particle_anim, self.position)
        super().destroy()

    def update(self):
        """
        매 프레임 업데이트:
        - 기본 이동 및 애니메이션 갱신
        - SOUL_EVIL_A 효과 시 추가 이동
        - 적과 충돌 검사, 대미지 처리 및 탄환 파괴
        """
        super().update()

        ps = self.scene.player_status
        
        # SOUL_EVIL_A 효과로 탄환 추가 이동
        if SOUL_EVIL_A in ps.soul_queue:
            self.position += self.direction * EVIL_A_PROJECTILE_SPEED_UP * self.app.dt
        
        from scripts.enemies import ALL_ENEMY_TYPE  # 순환 참조 회피용 임포트
        
        all_enemies = self.scene.get_objects_by_types(ALL_ENEMY_TYPE)

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
import pygame as pg
import json

from scripts.constants import *
from scripts.utils import *
from scripts.camera import *
from scripts.vfx import *
from scripts.ui import *

# 탄환 데이터 파일 경로
DATA_PATH = "data/projectile_data.json"

# 탄환 데이터 JSON 파일에서 모두 불러오기
with open(DATA_PATH, 'r', encoding="utf-8") as f:
    ALL_PROJECTILE_DATA = json.load(f)

class Projectile(GameObject):
    """
    탄환의 기본 클래스
    새로운 탄환 클래스를 만들 때 이 클래스를 상속받아 사용

    Args:
        projectile_name (str): 탄환 종류 키값 (탄환 데이터 불러올 때 사용)
        start_position (pg.Vector2): 탄환 생성 위치 (보통 발사체의 중심 좌표)
        start_direction (pg.Vector2): 탄환 이동 방향 (벡터)
        life_time (float, optional): 탄환 수명(초)
    """
    def __init__(self, projectile_name: str,
                 start_position: pg.Vector2, start_direction: pg.Vector2,
                 life_time: float, destroy_on_tilemap_collision : bool = True):
        super().__init__()

        # 탄환 기본 데이터(속도, 대미지 등) 불러오기
        self.data = ALL_PROJECTILE_DATA[projectile_name]
        self.destroy_on_tilemap_collision = destroy_on_tilemap_collision

        self.position = start_position
        self.direction = start_direction

        # 탄환 애니메이션 복사본 생성
        self.anim: Animation = self.app.ASSETS["animations"]["projectiles"][projectile_name].copy()

        # 탄환 수명 타이머 설정, 끝나면 자동 파괴
        self.timer = Timer(life_time, lambda: self.destroy())

    def destroy(self):
        """
        파괴 처리: 타이머 종료, 파티클 생성, 부모 파괴 호출
        """
        self.timer.destroy()
        super().destroy()

    def update_tilemap_collision(self):
        """
        현재 위치 주변 타일맵 타일들과 충돌 검사
        충돌 시 탄환 파괴
        """
        if not self.destroy_on_tilemap_collision:
            return
        for rect in self.scene.tilemap_data.physic_tiles_around(self.position):
            if rect.collidepoint(self.position):
                self.destroy()
                break

    def update(self):
        """
        매 프레임 호출, 탄환 위치 갱신 및 애니메이션, 충돌 검사 수행
        """
        super().update()

        # 방향과 속도에 따른 위치 이동 (프레임 독립적)
        self.position += self.direction * self.data["speed"] * self.app.dt

        # 애니메이션 프레임 갱신
        self.anim.update(self.app.dt)

        # 타일맵 충돌 처리
        self.update_tilemap_collision()
        
    def draw(self):
        """
        화면에 탄환 애니메이션 이미지를 현재 위치에 그리기
        카메라 좌표계로 변환하며 회전된 이미지를 사용
        """
        super().draw()

        surface = self.app.surfaces[LAYER_DYNAMIC]
        camera = self.scene.camera

        image = self.anim.img()

        # 이동 방향 벡터에 따른 회전 각도 계산 (기본 x축 벡터 기준)
        angle = self.direction.angle_to(pg.Vector2(1, 0))

        # 애니메이션 이미지 회전
        rotated_img = pg.transform.rotate(image, angle)

        # 이미지 중앙 기준 위치 조정
        draw_pos = self.position - pg.Vector2(rotated_img.get_size()) * 0.5
        screen_pos = CameraMath.world_to_screen(camera, draw_pos)

        surface.blit(rotated_img, screen_pos)

class EnemyProjectile(Projectile):
    def __init__(self, projectile_name, start_position, start_direction, life_time,
                 destroy_on_tilemap_collision : bool = True, destroy_on_player_collision : bool = True, corrupt_on_attack : bool = False):
        super().__init__(projectile_name, start_position, start_direction, life_time, destroy_on_tilemap_collision)
        
        self.destroy_on_player_collision = destroy_on_player_collision
        self.corrupt_on_attack = corrupt_on_attack

    def attack_corruption(self):
        if not self.corrupt_on_attack:
            return
        
        ps = self.scene.player_status

        # 무적이 아니고, 큐가 비어있지 않고, 전부 DEFAULT가 아닐 때만 실행
        if ps.current_invincible_time <= 0 and ps.soul_queue and not all(soul == SOUL_DEFAULT for soul in ps.soul_queue):
            for i in range(len(ps.soul_queue)):
                ps.soul_queue[i] = SOUL_DEFAULT  # 값 교체
            self.scene.event_bus.emit("on_player_soul_changed")
            AnimatedParticle(self.app.ASSETS["animations"]["vfxs"]["darkness"], pg.Vector2(ps.player_character.rect.center))
            PopupText(
                "혼이 감염되어 소멸해버렸다...",
                pg.Vector2(SCREEN_SIZE.x / 2, 680),
                fade_delay=.25,
                fade_duration=1.5
            )

    def update_player_collision(self):
        ps = self.scene.player_status
        pc = ps.player_character

        if pc.rect.collidepoint(self.position):
            ps.health -= self.data["damage"]
            self.scene.event_bus.emit("on_player_hurt", self.data["damage"])
            self.attack_corruption()

            if self.destroy_on_player_collision:
                self.destroy()
        
    def update(self):
        if not hasattr(self.scene, "player_status"):
            return
        super().update()
        self.update_player_collision()
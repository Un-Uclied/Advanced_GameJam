import pygame as pg
import json

from scripts.constants import *
from scripts.camera import *


#5초가 지나면 자동으로 삭제
TIME_OUT = 5
DATA_PATH = "data/projectile_data.json"

# Projectile 생성할때 대미지나 속도 같은게 인수로 들어오면 더러워져서 여기서 모든 탄환 데이터 로드
with open(DATA_PATH, 'r') as f:
    data = json.load(f)
    ALL_PROJECTILE_DATA = data

from scripts.objects import GameObject
class Projectile(GameObject):
    '''
    다른 탄환 클래스의 부모 클래스
    새로운 탄환을 만들꺼면 이 클래스를 상속 받아서 만들기 (예: PlayerProjectile(Projectile) )

    :param projectile_name: 탄환 데이터의 키 (중요)
    :param start_position: 시작 위치!! (대개로 pg.Vector2(엔티티.rect.center))
    :param start_direction: 탄환 방향!!
    '''

    def __init__(self, projectile_name : str,
                 start_position : pg.Vector2, start_direction : pg.Vector2):
        super().__init__()

        #여기에 속도, 대미지가 들어가 있음
        self.data = ALL_PROJECTILE_DATA[projectile_name]

        self.position = start_position
        self.direction = start_direction

        self.time_out_timer = TIME_OUT

        # 탄환 애니메이션
        self.anim = self.app.ASSETS["animations"]["projectiles"][projectile_name].copy()

    def update(self):
        super().update()

        # 방향에 맞게 업데이트
        self.position += self.direction * self.data["speed"] * self.app.dt

        # 탄환 애니메이션 업데이트
        self.anim.update(self.app.dt)

        # 일정 시간 지나면 자동으로 삭제
        self.time_out_timer -= self.app.dt
        if self.time_out_timer <= 0:
            self.destroy()

        # 타일맵과 닿으면 삭제
        for rect in self.app.scene.tilemap.physic_tiles_around(self.position):
            if rect.collidepoint(self.position):
                self.destroy()
                break

    def draw(self):
        super().draw()

        # LAYER_DYNAMIC는 안개가 덮히지 않는 파티클, 탄환이 그려지는 레이어
        surface = self.app.surfaces[LAYER_DYNAMIC]
        camera = self.app.scene.camera

        image = self.anim.img()

        # 방향에 맞게 앵글 갖고오고
        angle = self.direction.angle_to(pg.Vector2(1, 0))

        # 애니메이션의 현재 이미지를 돌림 => 그리고 이미지 크기 카메라에 맞게 조절
        rotated_img = pg.transform.rotate(image, angle)

        #이미지 중앙에 그리기 (앵커가 중앙)
        draw_pos = self.position - pg.Vector2(rotated_img.get_size()) * 0.5
        screen_pos = CameraMath.world_to_screen(camera, draw_pos)

        surface.blit(rotated_img, screen_pos)
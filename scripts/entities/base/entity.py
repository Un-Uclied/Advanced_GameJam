import pygame as pg

from scripts.constants import *
from scripts.objects import GameObject
from scripts.camera import *

class Entity(GameObject):
    def __init__(self, name : str, rect : pg.Rect, start_action : str = "idle", invert_x : bool = False):
        super().__init__()
        self.name : str = name
        self.rect : pg.Rect = rect

        # frame_movement는 PhysicsEntity에서 직접적인 움직임을 주지만, Entity는 움직이진 않고, 이미지 반전에만 상관관계가 있기때문에
        # Entity를 상속 받는 클래스에서 자기 자신을 frame_movement에 맞게 움직이고 싶다면 직접 rect.x += movement.x이렇게 해야함.
        self.movement : pg.Vector2 = pg.Vector2()

        # 시작 애니메이션
        self.current_action : str = ""
        self.set_action(start_action)

        # 에셋마다 기본으로 왼쪽을 볼수도 있고 오른쪽을 볼수도 있는 중구 난방 상태라서 invert_x를 만듦
        self.invert_x = invert_x
        self.flip_x : bool = False
        # 이미지를 그릴때 위치가 어긋나는것을 고치기 위해 뒤집혔을때랑 안뒤집혔을때 각각 셋팅 가능 
        self.flip_offset : dict[bool, pg.Vector2] = {
            False : pg.Vector2(0, 0),
            True : pg.Vector2(0, 0)
        }

    def set_action(self, action_name):
        #이미 같은 액션중이면 바로 리턴
        if self.current_action == action_name : return

        # 현재 애니메이션 바꾸기
        self.current_action = action_name
        self.anim = self.app.ASSETS["animations"]["entities"][self.name][action_name].copy()

    def get_rect_points(self) -> list[pg.Rect]:
        '''히트박스 꼭짓점들 반환'''
        points = []
        for point in [self.rect.topleft, self.rect.topright, self.rect.bottomleft, self.rect.bottomright]:
            points.append(pg.Vector2(point))
        return points
    
    def update(self):
        super().update()

        # 애니메이션 직접 관리
        self.anim.update(self.app.dt)

        # frame_movement에 따라 이미지 반전
        # (movement.y는 무시)
        if self.movement.x < 0:
            self.flip_x = False if self.invert_x else True
        elif self.movement.x > 0:
            self.flip_x = True if self.invert_x else False

    def draw_debug(self):
        super().draw_debug()
        
        # 콜리션 rect에 맞게 외곽선으로 그리기
        pg.draw.rect(self.app.surfaces[LAYER_INTERFACE], "yellow", CameraView.world_rect_to_screen(self.app.scene.camera, self.rect), width=2)

    def draw(self):
        super().draw()

        camera = self.app.scene.camera

        # 현재 애니메이션 이미지 얻기
        image = self.anim.img()
        flipped_image = pg.transform.flip(image, self.flip_x, False)

        # 현재 위치 계산 (좌표 보정 포함)
        world_position = pg.Vector2(self.rect.topleft) + self.flip_offset[self.flip_x]
        image_rect = pg.Rect(world_position, image.get_size())

        # 컬링 처리: 화면 밖이면 안 그림
        if not CameraView.is_in_view(camera, image_rect):
            return

        # 실제 스크린 위치 계산
        position = CameraMath.world_to_screen(camera, world_position)

        # 렌더링
        self.app.surfaces[LAYER_ENTITY].blit(flipped_image, position)
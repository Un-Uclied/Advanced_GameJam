import pygame as pg

from scripts.constants import *
from scripts.objects import GameObject
from scripts.camera import *

class Entity(GameObject):
    def __init__(self, name : str, rect : pg.Rect, start_action : str = "idle", invert_x : bool = False):
        super().__init__()
        self.name : str = name
        self.rect : pg.Rect = rect

        self.frame_movement : pg.Vector2 = pg.Vector2()

        self.current_action : str = ""
        self.set_action(start_action)

        self.invert_x = invert_x
        self.flip_x : bool = False
        self.flip_offset : dict[bool, pg.Vector2] = {
            False : pg.Vector2(0, 0),
            True : pg.Vector2(0, 0)
        }

    def set_action(self, action_name):
        if self.current_action == action_name : return

        self.current_action = action_name
        self.anim = self.app.ASSETS["animations"]["entities"][self.name][action_name].copy()

    def get_rect_points(self):
        points = []
        for point in [self.rect.topleft, self.rect.topright, self.rect.bottomleft, self.rect.bottomright]:
            points.append(pg.Vector2(point))
        return points
    
    def update(self):
        super().update()
        self.anim.update(self.app.dt)
        if self.frame_movement.x < 0:
            self.flip_x = False if self.invert_x else True
        elif self.frame_movement.x > 0:
            self.flip_x = True if self.invert_x else False

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

        # 스케일 처리
        surface = CameraView.get_scaled_surface(camera, flipped_image)

        # 실제 스크린 위치 계산
        position = CameraMath.world_to_screen(camera, world_position)

        # 렌더링
        self.app.surfaces[LAYER_ENTITY].blit(surface, position)
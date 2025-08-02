import pygame as pg

from scripts.constants import *
from scripts.camera import *
from scripts.core import *

class Entity(GameObject):
    def __init__(self, name: str, rect: pg.Rect, start_action: str = "idle", invert_x: bool = False):
        super().__init__()

        self.name = name
        self.rect = rect

        self.movement = pg.Vector2()

        self.current_action: str = ""
        self.invert_x = invert_x
        self.flip_x: bool = False

        self.flip_offset: dict[bool, pg.Vector2] = {
            False: pg.Vector2(0, 0),
            True: pg.Vector2(0, 0)
        }

        self.set_action(start_action)

    def set_action(self, action_name: str):
        if self.current_action == action_name:
            return

        self.current_action = action_name
        self.anim = self.app.ASSETS["animations"]["entities"][self.name][action_name].copy()

    def get_rect_points(self) -> list[pg.Vector2]:
        '''히트박스의 꼭짓점 좌표를 반환'''
        return [
            pg.Vector2(self.rect.topleft),
            pg.Vector2(self.rect.topright),
            pg.Vector2(self.rect.bottomleft),
            pg.Vector2(self.rect.bottomright)
        ]

    def update(self):
        super().update()

        # flip 방향 결정
        if self.movement.x < 0:
            self.flip_x = not self.invert_x
        elif self.movement.x > 0:
            self.flip_x = self.invert_x

        # flip 적용
        self.anim.flip_x = self.flip_x
        self.anim.update(self.app.dt)

    def draw_debug(self):
        super().draw_debug()
        pg.draw.rect(
            self.app.surfaces[LAYER_INTERFACE],
            "yellow",
            CameraView.world_rect_to_screen(self.app.scene.camera, self.rect),
            width=2
        )

    def draw(self):
        super().draw()

        cam = self.app.scene.camera

        img = self.anim.img()
        world_pos = pg.Vector2(self.rect.topleft) + self.flip_offset[self.flip_x]
        img_rect = pg.Rect(world_pos, img.get_size())

        if not CameraView.is_in_view(cam, img_rect):
            return

        screen_pos = CameraMath.world_to_screen(cam, world_pos)
        self.app.surfaces[LAYER_ENTITY].blit(img, screen_pos)
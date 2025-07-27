import pygame as pg

from scripts.constants import *
from scripts.objects import *
from scripts.camera import *

LIGHT_SEGMENTS = 15 #원 모양이 그려지는 횟수
LIGHT_FADE_OUT = 10 #빛의 알파값이 점점 줄어드는 양 

class Light(GameObject):
    def __init__(self, size : float, position : pg.Vector2, strength : float = 25):
        super().__init__()

        self.position = position
        #성능을 위해 생성시 딱 한번만 surface를 만듦. | 그래서 self.size를 선언하지 않음 => 런타임중 바꿀수 없음.
        self.surface = pg.Surface((size, size), pg.SRCALPHA)

        for i in range(LIGHT_SEGMENTS):
            alpha = min(i * strength, 255)
            pg.draw.circle(
                self.surface,
                (255, 255, 255, alpha),
                (size / 2, size / 2),
                size / 2 - i * LIGHT_FADE_OUT
            )

    @property
    def bound_box(self):
        '''월드 rect를 반환'''
        bound_box = pg.Rect(self.position, self.surface.get_size())
        bound_box.center = self.position  #이렇게 해야 빛의 중앙이 position으로 맞춰짐.
        return bound_box

    @classmethod
    def draw_lights(cls, camera : Camera2D, surface: pg.Surface):
        '''받은 surface에 BLEND_RGBA_SUB로 빛 효과를 냄 (surface에 구멍을 뚫음)'''
        all_lights = GameObject.get_objects_by_types([Light])
        for light in all_lights:
            #최적화를 위해 화면 밖에 있으면 건너뜀.
            if not CameraView.is_in_view(camera, light.bound_box): continue

            rect = CameraView.world_rect_to_screen(camera, light.bound_box)
            surface.blit(CameraView.get_scaled_surface(camera, light.surface), rect.topleft, special_flags=pg.BLEND_RGBA_SUB)
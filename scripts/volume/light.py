import pygame as pg

from scripts.constants import *
from scripts.camera import *
from scripts.core import *

LIGHT_SEGMENTS = 15 #원 모양이 그려지는 횟수
LIGHT_FADE_OUT = 10 #원 모양이 작아지는 양

class Light(GameObject):
    '''
    size & strength는 런타임중에 바꿀수 없음, 위치는 언제든지 변경 가능
    
    :param size: 빛 Surface의 월드 좌표계 크기
    :param position: 빛 Surface의 중앙 위치
    :param strength: 빛 알파값
    '''
    
    def __init__(self, size : float, position : pg.Vector2, strength : float = 25):
        super().__init__()

        self.position = position
        #성능을 위해 생성시 딱 한번만 Surface를 만듦. | 그래서 self.size를 선언하지 않음 => 런타임중 바꿀수 없음.
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
            surface.blit(light.surface, rect.topleft, special_flags=pg.BLEND_RGBA_SUB)
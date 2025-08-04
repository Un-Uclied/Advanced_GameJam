import pygame as pg

from scripts.constants import *
from scripts.camera import *
from scripts.core import *

class ImageRenderer(GameObject):
    '''
    베리 베리 간단한 UI용 이미지 렌더러 (포지션, scale Tween가능 ㅇㅇ)

    :param image: 렌더할 이미지 (절대 에셋 키 아님!! pg.Surface여야함!! (직접 이미지에 접근 하라는뜻 ㅇㅇ))
    :param position: 렌더할 위치 (스크린 좌표)
    :param scale: 렌더할 이미지의 스케일 (기본값 1, 에셋 로드 할때 이미 스케일을 바꿨다면 바꾼 상태에서 또 scale하는거임)
    :param anchor: 렌더할 이미지의 앵커 (기본값은 중앙, 0.5, 0.5)
    '''
    def __init__(self, image : pg.Surface, position : pg.Vector2, scale : float = 1, anchor : pg.Vector2 = pg.Vector2(.5, .5), use_camera = False):
        super().__init__()
        self.image = image
        self.scale = scale
        self.pos = position
        self.anchor = anchor
        self.use_camera = use_camera

    @property
    def size(self) -> pg.Vector2:
        '''현재 렌더되는 이미지 크기 (트윈 할거면 scale을 트윈하세여!!)'''
        return pg.Vector2(self.image.get_size()) * self.scale

    @property
    def screen_pos(self) -> pg.Vector2:
        '''앵커를 계산한 렌더 위치'''
        return self.pos - self.size.elementwise() * self.anchor

    @property
    def rect(self) -> pg.Rect:
        '''마우스 충돌 판정 rect'''
        return pg.Rect(self.screen_pos, self.size)

    def draw(self):
        super().draw()

        surface = self.app.surfaces[LAYER_INTERFACE]
        scaled_image = pg.transform.scale_by(self.image, self.scale)

        draw_pos = self.screen_pos
        if self.use_camera:
            draw_pos = CameraMath.world_to_screen(self.app.scene.camera, draw_pos)
            
        surface.blit(scaled_image, draw_pos)
import pygame as pg

from scripts.constants import *
from scripts.camera import *
from scripts.core import *

class ProgressBar(GameObject):
    '''
    베리베리 간단한 바 (체력바나 로딩 바에 가능 ㅇㅇ)
    (경고 : 가로만 됨!! 세로 바는 안됨 ㅇㅇ;)
    :param pos: 위치
    :param size: 두께, 높이
    :param current_val: 시작하는 값
    :param min_val: 최소값 (0이 제일 일반적)
    :param max_val: 최대값
    :param bg_color: 바의 배경색
    :param fg_color: 바의 색깔
    :param anchor: 그냥 앵커 (기본은 중앙인데, (0, .5)쓰거나 뭐 다양하게 가능)
    '''
    def __init__(self,
                 pos: pg.Vector2,
                 size: pg.Vector2,
                 current_val : float,
                 min_val : float,
                 max_val : float,
                 bg_color = pg.Color("grey"),
                 fg_color = pg.Color("red"),
                 anchor: pg.Vector2 = pg.Vector2(0.5, 0.5), use_camera = False):
        super().__init__()

        self._pos = pos
        self.size = size
        self.anchor = anchor

        self.min_val = min_val
        self.max_val = max_val
        self._val = max(min(current_val, max_val), min_val)

        self.bg_color = bg_color
        self.fg_color = fg_color

        self.bg_rect = pg.Rect((0, 0), size)
        self.fg_rect = pg.Rect((0, 0), size)

        self.use_camera = use_camera

        self.update_rects()
    
    @property
    def value(self):
        return self._val
    
    @value.setter
    def value(self, change_val):
        self._val = max(min(change_val, self.max_val), self.min_val)
        self.update_rects()

    @property
    def pos(self):
        return self._pos
    
    @pos.setter
    def pos(self, value):
        self._pos = value
        self.update_rects()

    def get_anchored_pos(self) -> pg.Vector2:
        return self._pos - self.size.elementwise() * self.anchor

    def update_rects(self):
        '''위치나 값 바뀌었을때 부르기!'''
        anchor_pos = self.get_anchored_pos()
        self.bg_rect.topleft = anchor_pos
        self.fg_rect.topleft = anchor_pos

        self.fg_rect.w = self.size.x * (self.value / self.max_val)

    def draw(self):
        super().draw()
        surface = self.app.surfaces[LAYER_INTERFACE]

        bg_rect = self.bg_rect.copy()
        fg_rect = self.fg_rect.copy()

        if self.use_camera:
            bg_rect.topleft = CameraMath.world_to_screen(self.app.scene.camera, pg.Vector2(bg_rect.topleft))
            fg_rect.topleft = CameraMath.world_to_screen(self.app.scene.camera, pg.Vector2(fg_rect.topleft))

        pg.draw.rect(surface, self.bg_color, bg_rect)
        pg.draw.rect(surface, self.fg_color, fg_rect)
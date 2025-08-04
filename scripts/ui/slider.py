import pygame as pg

from scripts.constants import *
from scripts.core import *

class Slider(GameObject):
    """
    슬라이더 UI 컴포넌트.

    :param pos: 슬라이더 중심 좌표
    :param size: (width, height)
    :param init_val: 초기값 (min_val ~ max_val 사이)
    :param min_val: 최소값
    :param max_val: 최대값
    :param anchor: 기준점 (0,0 = 좌상단 / 0.5,0.5 = 중앙)
    """

    def __init__(self,
                 pos: pg.Vector2,
                 size: pg.Vector2,
                 init_val: float = .5,
                 min_val: float = 0,
                 max_val: float = 1,
                 on_value_changed = None,
                 anchor: pg.Vector2 = pg.Vector2(0.5, 0.5)):
        super().__init__()

        self.pos = pos
        self.size = size
        self.anchor = anchor

        self.min_val = min_val
        self.max_val = max_val
        self.value = max(min(init_val, max_val), min_val)

        self.btn_size = pg.Vector2(30, size.y + 10)
        self.dragging = False
        self.hovering = False
        self.on_value_changed = on_value_changed

        self.bg_rect = pg.Rect(0, 0, size.x, size.y)
        self.btn_rect = pg.Rect(0, 0, self.btn_size.x, self.btn_size.y)

        self.update_rects()

    @property
    def percentage(self) -> float:
        """0 ~ 1 사이의 퍼센트 반환 (읽기 전용)"""
        return (self.value - self.min_val) / (self.max_val - self.min_val)

    def set_value(self, new_value: float):
        """슬라이더 값을 외부에서 설정"""
        self.value = max(min(new_value, self.max_val), self.min_val)
        self.update_rects()

    def get_anchored_pos(self) -> pg.Vector2:
        return self.pos - self.size.elementwise() * self.anchor

    def update_rects(self):
        bg_pos = self.get_anchored_pos()
        self.bg_rect.topleft = bg_pos

        percent = self.percentage
        btn_center_x = self.bg_rect.left + self.size.x * percent
        btn_center_y = self.bg_rect.centery

        self.btn_rect.size = self.btn_size
        self.btn_rect.center = (btn_center_x, btn_center_y)

    def update(self):
        super().update()

        mouse_pos = pg.mouse.get_pos()
        mouse_down = pg.mouse.get_pressed()[0]

        if self.bg_rect.collidepoint(mouse_pos) and mouse_down:
            self.dragging = True
        elif not mouse_down:
            self.dragging = False

        if self.dragging:
            clamped_x = max(self.bg_rect.left, min(mouse_pos[0], self.bg_rect.right))
            percent = (clamped_x - self.bg_rect.left) / self.size.x
            self.value = self.min_val + percent * (self.max_val - self.min_val)
            self.update_rects()
            if self.on_value_changed is not None:
                self.on_value_changed()

        self.hovering = self.bg_rect.collidepoint(mouse_pos)

    def draw(self):
        super().draw()
        surface = self.app.surfaces[LAYER_INTERFACE]
        pg.draw.rect(surface, pg.Color("gray"), self.bg_rect)
        pg.draw.rect(surface, pg.Color("white"), self.btn_rect)
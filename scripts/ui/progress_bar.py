import pygame as pg

from scripts.constants import *
from scripts.camera import *
from scripts.utils import *

class ProgressBar(GameObject):
    """
    심플한 가로형 프로그레스 바 (체력바, 로딩바 등 용)

    특징:
    - 가로 방향만 지원 (세로 바는 따로 만들어야 함)
    - 값 변경 시 자동으로 표시 갱신
    - 앵커 설정 가능 (기본 중앙)
    - 월드 좌표 기준(use_camera=True) 옵션 지원

    Args:
        pos (pg.Vector2): 기준 위치 (앵커 기준)
        size (pg.Vector2): 크기 (가로 너비, 세로 높이)
        current_val (float): 초기 값 (min_val ~ max_val 사이)
        min_val (float): 최소값 (보통 0)
        max_val (float): 최대값
        bg_color (pg.Color): 배경 바 색상 (기본 회색)
        fg_color (pg.Color): 채워진 바 색상 (기본 빨강)
        anchor (pg.Vector2): 앵커 기준점 (0~1, 기본 중앙 (0.5, 0.5))
        use_camera (bool): 월드 좌표 기반 여부 (기본 False)
    """
    def __init__(self,
                 pos: pg.Vector2,
                 size: pg.Vector2,
                 current_val: float,
                 min_val: float,
                 max_val: float,
                 bg_color=pg.Color("grey"),
                 fg_color=pg.Color("red"),
                 anchor: pg.Vector2 = pg.Vector2(0.5, 0.5),
                 use_camera: bool = False):
        super().__init__()

        self._pos = pos
        self.size = size
        self.anchor = anchor

        self.min_val = min_val
        self.max_val = max_val
        self._value = max(min(current_val, max_val), min_val)

        self.bg_color = bg_color
        self.fg_color = fg_color

        self.use_camera = use_camera

        self.bg_rect = pg.Rect((0, 0), size)
        self.fg_rect = pg.Rect((0, 0), size)

        self._update_rects()

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, new_val: float):
        self._value = max(min(new_val, self.max_val), self.min_val)
        self._update_rects()

    @property
    def pos(self) -> pg.Vector2:
        return self._pos

    @pos.setter
    def pos(self, new_pos: pg.Vector2):
        self._pos = new_pos
        self._update_rects()

    def _get_anchored_pos(self) -> pg.Vector2:
        """앵커를 고려한 실제 좌표 계산"""
        return self._pos - self.size.elementwise() * self.anchor

    def _update_rects(self):
        """값이나 위치 변경 시 호출: rect 위치 및 크기 업데이트"""
        anchored_pos = self._get_anchored_pos()
        self.bg_rect.topleft = anchored_pos
        self.fg_rect.topleft = anchored_pos

        fill_ratio = (self._value - self.min_val) / (self.max_val - self.min_val) if self.max_val != self.min_val else 0
        self.fg_rect.width = self.size.x * fill_ratio

    def draw(self):
        super().draw()
        surface = self.app.surfaces[LAYER_INTERFACE]

        bg_rect = self.bg_rect.copy()
        fg_rect = self.fg_rect.copy()

        if self.use_camera:
            bg_rect.topleft = CameraMath.world_to_screen(self.scene.camera, pg.Vector2(bg_rect.topleft))
            fg_rect.topleft = CameraMath.world_to_screen(self.scene.camera, pg.Vector2(fg_rect.topleft))

        pg.draw.rect(surface, self.bg_color, bg_rect)
        pg.draw.rect(surface, self.fg_color, fg_rect)
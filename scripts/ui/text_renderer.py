import pygame as pg

from scripts.constants import *
from scripts.camera import *
from scripts.core import *

BASE_FONT_PATH = "assets/fonts/"

class TextRenderer(GameObject):
    """
    스크린 기준 UI 텍스트 렌더러.

    - text, position, color는 런타임 중 변경 가능
    - 폰트 종류와 크기는 생성 시 고정 (성능상 이유)
    - use_camera=True면 월드 좌표 사용하며 카메라 이펙트 받음

    :param start_text: 초기 텍스트 내용
    :param position: 텍스트 위치 (pg.Vector2)
    :param font_name: 사용할 폰트 이름 (ASSETS["fonts"] 키)
    :param font_size: 폰트 크기
    :param color: 텍스트 색상
    :param anchor: 기준점 (0,0=좌상단, 0.5,0.5=중앙 등)
    :param use_camera: 카메라 적용 여부
    """
    def __init__(self,
                 start_text: str,
                 position: pg.Vector2,
                 font_name: str = "default",
                 font_size: int = 24,
                 color: pg.Color = pg.Color("white"),
                 anchor: pg.Vector2 = pg.Vector2(0, 0),
                 use_camera: bool = False):
        super().__init__()

        self._text = start_text
        self.pos = position
        self.anchor = anchor
        self.use_camera = use_camera

        self._color = pg.Color(color)
        self._alpha = 255
        self._scale = 1  # Tween용

        font_path = BASE_FONT_PATH + self.app.ASSETS["fonts"][font_name]
        self.font = pg.font.Font(font_path, font_size)

        self.image = self.font.render(self.text, True, self._color)
        self.image.set_alpha(self._alpha)

    @property
    def scale(self):
        return self._scale
    
    @scale.setter
    def scale(self, value):
        if self._scale == value:
            return
        self._scale = value
        self.rerender()

    @property
    def size(self) -> pg.Vector2:
        '''스케일 포함된 이미지 크기 반환함'''
        return pg.Vector2(self.image.get_size())

    @property
    def screen_pos(self) -> pg.Vector2:
        '''앵커 계산해서 실제 화면에 그릴 좌표 반환함'''
        return self.pos - self.size.elementwise() * self.anchor

    @property
    def rect(self) -> pg.Rect:
        '''마우스랑 충돌 체크할 때 쓰는 사각형 반환함'''
        return pg.Rect(self.screen_pos, self.size)

    @property
    def color(self) -> pg.Color:
        '''텍스트 색상 가져옴'''
        return self._color

    @color.setter
    def color(self, value: pg.Color):
        '''텍스트 색상 바꾸면 자동으로 다시 렌더됨'''
        self._color = pg.Color(value)
        self.rerender()

    @property
    def alpha(self) -> int:
        '''알파 값 반환 (0~255)'''
        return self._alpha

    @alpha.setter
    def alpha(self, value: int):
        '''알파 값 변경 (0~255로 제한)'''
        self._alpha = max(0, min(255, value))
        self.image.set_alpha(self._alpha)

    @property
    def text(self) -> str:
        '''텍스트 문자열 반환'''
        return self._text

    @text.setter
    def text(self, value: str):
        '''텍스트 바꾸면 자동으로 다시 렌더됨'''
        self._text = value
        self.rerender()

    def rerender(self):
        """텍스트나 색 바뀌면 호출해서 이미지 새로 만듦 (줄바꿈 지원)"""
        if not self._text.strip():
            self.image = pg.Surface((1, 1), pg.SRCALPHA)
            self.image.set_alpha(self._alpha)
            return
    
        lines = self._text.splitlines()
        line_surfaces = [self.font.render(line, False, self._color) for line in lines]

        width = max(surf.get_width() for surf in line_surfaces)
        height = sum(surf.get_height() for surf in line_surfaces)

        # 원본 텍스트 이미지를 먼저 합침
        base_image = pg.Surface((width, height), pg.SRCALPHA)
        y = 0
        for surf in line_surfaces:
            base_image.blit(surf, (0, y))
            y += surf.get_height()

        base_image.set_alpha(self._alpha)

        # 💥 여기서 스케일링 처리!
        if self.scale != 1:
            scaled_size = (round(base_image.get_width() * self.scale),
                           round(base_image.get_height() * self.scale))
            self.image = pg.transform.smoothscale(base_image, scaled_size)
        else:
            self.image = base_image

    def draw(self):
        '''앵커랑 스케일 계산해서 텍스트 그려줌'''
        super().draw()

        # 최적화 발악
        if self.alpha <= 0:
            return

        surface = self.app.surfaces[LAYER_INTERFACE]

        draw_pos = self.screen_pos
        if self.use_camera:
            draw_pos = CameraMath.world_to_screen(self.app.scene.camera, draw_pos)

        surface.blit(self.image, draw_pos)
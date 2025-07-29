import pygame as pg

from scripts.constants import *
from scripts.objects import GameObject

BASE_FONT_PATH = "assets/fonts/"

class TextRenderer(GameObject):
    """
    스크린 기준 UI 텍스트 렌더러.
    텍스트, 위치, 색상은 런타임 중 변경 가능하지만,
    폰트 종류와 크기는 생성 시 고정됨 (성능상 이유로)

    :param start_text: 초기 텍스트 내용
    :param pos: 텍스트의 스크린 위치 (pg.Vector2)
    :param font_name: 사용할 폰트 이름 (ASSETS["fonts"]에 등록된 키)
    :param font_size: 폰트 크기 (int)
    :param color: 텍스트 색상 (pg.Color)
    """

    def __init__(self,
                 start_text : str,
                 pos : pg.Vector2,
                 font_name : str = "default",
                 font_size : int = 24,
                 color : pg.Color = pg.Color(255, 255, 255),
                 anchor : pg.Vector2 = pg.Vector2(0, 0)):
        super().__init__()

        self.text = start_text
        self.pos = pos
        self.color = pg.Color(color)
        self.anchor = anchor
        self._alpha = 255

        self.font = pg.font.Font(BASE_FONT_PATH + self.app.ASSETS["fonts"][font_name], font_size)

    @property
    def alpha(self):
        return self._alpha
    
    @alpha.setter
    def alpha(self, value):
        # 0 ~ 255로 제한
        self._alpha = max(min(value, 255), 0)

    def draw(self):
        super().draw()
        surface = self.app.surfaces[LAYER_INTERFACE]

        # 알파는 render에 안 먹히니까 수동으로 Surface 조작
        text_surf = self.font.render(self.text, True, self.color)
        text_surf.set_alpha(self.alpha)

        # 앵커까지 계산
        screen_pos = self.pos - pg.Vector2(text_surf.get_size()).elementwise() * self.anchor

        surface.blit(text_surf, screen_pos)
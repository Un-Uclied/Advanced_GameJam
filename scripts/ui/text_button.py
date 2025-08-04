import pygame as pg
import pytweening as pt

from scripts.constants import *
from scripts.core import *
from .text_renderer import TextRenderer

class TextButton(GameObject):
    '''
    스크린 UI 텍스트 버튼 (hover, click, tween 지원)

    :param name: 버튼 이름 (애셋 키)
    :param position: 기준 위치
    :param on_click: 클릭시 실행될 함수 (self)
    :param on_hover: hover시 실행될 함수 (self, 상태 ("enter", "exit"))
    :param button: 사용할 마우스 버튼 (기본 1 = 좌클릭)
    :param anchor: 앵커 기준 (기본 중앙)
    '''
    def __init__(self, 
                 text : str,
                 position: pg.Vector2,
                 on_click = None, 
                 on_hover = None,
                 font_name = "default",
                 font_size = 24,
                 not_hover_color = pg.Color("white"),
                 hover_color = pg.Color("blue"),
                 button: int = 1,
                 anchor: pg.Vector2 = pg.Vector2(0.5, 0.5)):
        
        super().__init__()
        self.pos = position
        self.anchor = anchor
        self.button = button

        self.on_click = on_click
        self.on_hover = on_hover

        # 텍스트 렌더러 내부 포함
        self.not_hover_color = not_hover_color
        self.hover_color = hover_color
        self.renderer = TextRenderer(text, position, font_name, font_size, self.not_hover_color, anchor, False)

        # 사운드 로드
        self.hover_enter_sound = self.app.ASSETS["sounds"]["ui"]["button"]["hover_enter"]
        self.hover_exit_sound  = self.app.ASSETS["sounds"]["ui"]["button"]["hover_exit"]
        self.click_sound       = self.app.ASSETS["sounds"]["ui"]["button"]["click"]

        self._was_hovered = False

    @property
    def is_hovered(self) -> bool:
        '''마우스가 버튼 위에 있는가?'''
        mouse_pos = pg.Vector2(pg.mouse.get_pos())
        return self.renderer.rect.collidepoint(mouse_pos)

    def update(self):
        super().update()

        now_hovered = self.is_hovered

        # hover 상태 진입 or 나감
        if not self._was_hovered and now_hovered:
            if self.on_hover is not None:
                self.on_hover(self, "enter")
            self.renderer.color = self.hover_color
            self.app.sound_manager.play_sfx(self.hover_enter_sound)

        elif self._was_hovered and not now_hovered:
            if self.on_hover is not None:
                self.on_hover(self, "exit")
            self.renderer.color = self.not_hover_color
            self.app.sound_manager.play_sfx(self.hover_exit_sound)

        # 클릭 처리
        for event in self.app.events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == self.button and now_hovered:
                self.app.sound_manager.play_sfx(self.click_sound)
                if self.on_click is not None:
                    self.on_click(self)

        self._was_hovered = now_hovered

    def destroy(self):
        self.renderer.destroy()
        super().destroy()

    def draw_debug(self):
        super().draw_debug()
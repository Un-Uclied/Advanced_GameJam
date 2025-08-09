import pygame as pg
import pytweening as pt

from scripts.constants import *
from scripts.core import *
from .text_renderer import TextRenderer

class TextButton(GameObject):
    """
    스크린 UI 텍스트 버튼 클래스

    주요 기능:
    - 마우스 오버 시 색상 변경 및 사운드 재생
    - 클릭 시 사운드 재생 및 콜백 실행
    - 앵커 기준 위치 지정 가능

    Args:
        text (str): 버튼에 표시할 텍스트 내용
        position (pg.Vector2): 버튼 기준 위치 (앵커 기준)
        on_click (func): 클릭 시 호출 함수(self 인자 전달)
        on_hover (func): 호버 진입/이탈 시 호출 함수(self, 상태("enter"/"exit") 인자 전달)
        font_name (str): 텍스트 폰트 이름 (애셋 키)
        font_size (int): 텍스트 폰트 크기
        not_hover_color (pg.Color): 기본 텍스트 색상
        hover_color (pg.Color): 호버 시 텍스트 색상
        button (int): 사용할 마우스 버튼 번호 (기본 1=좌클릭)
        anchor (pg.Vector2): 앵커 기준점 (0~1 사이, 기본 중앙 0.5,0.5)
        data (dict): 추가 데이터 임의로 저장 가능
    """
    def __init__(self, 
                 text: str,
                 position: pg.Vector2,
                 on_click=None, 
                 on_hover=None,
                 font_name="default",
                 font_size=24,
                 not_hover_color=pg.Color("white"),
                 hover_color=pg.Color("blue"),
                 button: int = 1,
                 anchor: pg.Vector2 = pg.Vector2(0.5, 0.5),
                 data: dict = None):
        
        super().__init__()

        self.button = button
        self.data = data or {}

        self.on_click = on_click
        self.on_hover = on_hover

        self.not_hover_color = not_hover_color
        self.hover_color = hover_color

        # 텍스트 렌더러 생성
        self.renderer = TextRenderer(text, position, font_name, font_size, self.not_hover_color, anchor, use_camera=False)

        # 사운드 로드
        sounds = self.app.ASSETS["sounds"]["ui"]["button"]
        self.hover_enter_sound = sounds["hover_enter"]
        self.hover_exit_sound = sounds["hover_exit"]
        self.click_sound = sounds["click"]

        self._was_hovered = False

    @property
    def is_hovered(self) -> bool:
        """마우스가 버튼 위에 있는지 여부 반환"""
        mouse_pos = pg.Vector2(pg.mouse.get_pos())
        return self.renderer.rect.collidepoint(mouse_pos)

    def update(self):
        super().update()

        now_hovered = self.is_hovered

        # 호버 상태 변화 감지 및 색상 변경, 사운드 재생
        if not self._was_hovered and now_hovered:
            if self.on_hover:
                self.on_hover(self, "enter")
            self.renderer.color = self.hover_color
            self.app.sound_manager.play_sfx(self.hover_enter_sound)

        elif self._was_hovered and not now_hovered:
            if self.on_hover:
                self.on_hover(self, "exit")
            self.renderer.color = self.not_hover_color
            self.app.sound_manager.play_sfx(self.hover_exit_sound)

        # 클릭 처리
        for event in self.app.events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == self.button and now_hovered:
                self.app.sound_manager.play_sfx(self.click_sound)
                if self.on_click:
                    self.on_click(self)

        self._was_hovered = now_hovered

    def destroy(self):
        self.renderer.destroy()
        super().destroy()
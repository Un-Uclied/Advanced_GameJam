import pygame as pg
import pytweening as pt

from scripts.constants import *
from scripts.core import *
from .image_renderer import ImageRenderer  # 새로 만든 거 활용

class ImageButton(GameObject):
    '''
    스크린 UI 버튼 (hover, click, tween 지원)

    :param name: 버튼 이름 (애셋 키)
    :param position: 기준 위치
    :param on_click: 클릭시 실행될 함수 (name, self)
    :param on_hover: hover시 실행될 함수 (name, self, 상태 ("enter", "exit"))
    :param button: 사용할 마우스 버튼 (기본 1 = 좌클릭)
    :param anchor: 앵커 기준 (기본 중앙)
    '''
    def __init__(self, 
                 name: str, 
                 position: pg.Vector2, 
                 on_click = None, 
                 on_hover = None,
                 button: int = 1,
                 anchor: pg.Vector2 = pg.Vector2(0.5, 0.5)):
        
        super().__init__()
        self.name = name
        self.pos = position
        self.anchor = anchor
        self.button = button

        self.on_click = on_click
        self.on_hover = on_hover

        # 이미지 로드
        self.default_img = self.app.ASSETS["ui"]["image_button"][name]["on_not_hover"]
        self.hover_img   = self.app.ASSETS["ui"]["image_button"][name]["on_hover"]
        self._render_img = self.default_img

        # 이미지 렌더러 내부 포함
        self.renderer = ImageRenderer(self._render_img, self.pos, 1.0, self.anchor)

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
        self.renderer.update()

        now_hovered = self.is_hovered
        self._render_img = self.hover_img if now_hovered else self.default_img
        self.renderer.image = self._render_img

        # hover 상태 진입 or 나감
        if not self._was_hovered and now_hovered:
            if self.on_hover is not None:
                self.on_hover(self.name, self, "enter")
            self.app.sound_manager.play_sfx(self.hover_enter_sound)
            Tween(self.renderer, "scale", self.renderer.scale, 1.2, .2, pt.easeOutBack, use_unscaled_time=True)

        elif self._was_hovered and not now_hovered:
            if self.on_hover is not None:
                self.on_hover(self.name, self, "exit")
            Tween(self.renderer, "scale", self.renderer.scale, 1.0, .2, pt.easeInBack, use_unscaled_time=True)
            self.app.sound_manager.play_sfx(self.hover_exit_sound)

        # 클릭 처리
        for event in self.app.events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == self.button and now_hovered:
                self.app.sound_manager.play_sfx(self.click_sound)
                if self.on_click is not None:
                    self.on_click(self.name, self)

        self._was_hovered = now_hovered

    def destroy(self):
        self.renderer.destroy()
        super().destroy()
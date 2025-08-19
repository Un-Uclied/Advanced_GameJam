import pygame as pg
import pytweening as pt

from scripts.constants import *
from scripts.utils import *
from .image_renderer import ImageRenderer

class ImageButton(GameObject):
    """
    스크린 UI용 이미지 버튼 클래스

    주요 기능:
    - 마우스 오버(hover) 시 이미지 변경 및 사운드 재생
    - 클릭 시 사운드 재생 및 콜백 함수 실행
    - 호버 시 스케일 트윈 효과 적용
    - 앵커 기준 위치 지정 가능

    Args:
        name (str): 애셋 키에 해당하는 버튼 이름
        position (pg.Vector2): 버튼 기준 위치 (앵커 기준)
        on_click (func): 클릭 시 호출 함수(self 인자 전달)
        on_hover (func): 호버 진입/이탈 시 호출 함수(self, 상태("enter"/"exit") 인자 전달)
        button (int): 사용할 마우스 버튼 번호 (기본 1 = 좌클릭)
        anchor (pg.Vector2): 앵커 기준점 (0~1 사이, 기본 중앙 0.5,0.5)
        data (dict): 버튼에 붙일 추가 데이터 (임의 사용 가능)
    """
    def __init__(self, 
                 name: str, 
                 position: pg.Vector2, 
                 on_click=None, 
                 on_hover=None,
                 button: int = 1,
                 anchor: pg.Vector2 = pg.Vector2(0.5, 0.5),
                 data: dict = None):
        
        super().__init__()

        self.name = name
        self.pos = position
        self.anchor = anchor
        self.button = button
        self.data = data or {}

        self.on_click = on_click
        self.on_hover = on_hover

        # 이미지 애셋 로드
        ui_assets = self.app.ASSETS["ui"]["image_button"][name]
        self.default_img = ui_assets["on_not_hover"]
        self.hover_img = ui_assets["on_hover"]

        self._render_img = self.default_img

        # 이미지 렌더러 생성 (스케일 기본 1.0)
        self.renderer = ImageRenderer(self._render_img, self.pos, 1.0, self.anchor)

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

        # 이미지 변경
        self._render_img = self.hover_img if now_hovered else self.default_img
        self.renderer.image = self._render_img

        # 호버 상태 변화 감지
        if not self._was_hovered and now_hovered:
            if self.on_hover:
                self.on_hover(self, "enter")
            self.app.sound_manager.play_sfx(self.hover_enter_sound)
            Tween(self.renderer, "scale", self.renderer.scale, 1.2, 0.2, pt.easeOutBack, use_unscaled_time=True)

        elif self._was_hovered and not now_hovered:
            if self.on_hover:
                self.on_hover(self, "exit")
            Tween(self.renderer, "scale", self.renderer.scale, 1.0, 0.2, pt.easeInBack, use_unscaled_time=True)
            self.app.sound_manager.play_sfx(self.hover_exit_sound)

        # 클릭 이벤트 처리
        for event in self.app.events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == self.button and now_hovered:
                self.app.sound_manager.play_sfx(self.click_sound)
                if self.on_click:
                    self.on_click(self)

        self._was_hovered = now_hovered

    def destroy(self):
        self.renderer.destroy()
        super().destroy()
import pygame as pg
import pytweening as tween

from scripts.constants import *
from scripts.vfx import Tween

from scripts.objects import GameObject
class ImageButton(GameObject):
    '''스크린 기준 UI 버튼

    :param name: 버튼 이름 (애셋 키)
    :param position: 버튼 기준 위치
    :param on_click: 클릭시 실행될 함수 (name, self 전달됨)
    :param on_hover: 클릭시 실행될 함수 (name, self, 상태 ("enter", "exit" 중하나) 전달됨)
    :param button: 사용할 마우스 버튼 (1=좌클릭, 3=우클릭 등)
    :param anchor: 버튼 기준점 (0~1) (0,0=좌상단 / 0.5,0.5=중앙)
    '''
    
    def __init__(self, 
                 name : str, 
                 position : pg.Vector2, 
                 on_click,
                 on_hover,
                 button : int = 1,
                 anchor : pg.Vector2 = pg.Vector2(0, 0)):
        
        super().__init__()
        self.name = name
        self.pos = position
        self.anchor = anchor
        self.button = button

        self.on_click = on_click
        self.on_hover = on_hover
        
        # 이미지 로드
        self.hover_image = self.app.ASSETS["ui"]["image_button"][name]["on_hover"]
        self.default_image = self.app.ASSETS["ui"]["image_button"][name]["on_not_hover"]
        self.render_image = self.default_image

        # 사운드 로드
        self.hover_enter_sound = self.app.ASSETS["sounds"]["ui"]["button"]["hover_enter"]
        self.hover_exit_sound  = self.app.ASSETS["sounds"]["ui"]["button"]["hover_exit"]
        self.click_sound       = self.app.ASSETS["sounds"]["ui"]["button"]["click"]

        # 이전 프레임의 hover 상태 기억
        self._was_hovered = False

        # 트윈용으로 하나 만듦
        self.scale = 1

    @property
    def size(self) -> pg.Vector2:
        '''현재 렌더되는 이미지 크기 (트윈 할거면 scale을 트윈하세여!!)'''
        return pg.Vector2(self.render_image.get_size()) * self.scale

    @property
    def screen_pos(self) -> pg.Vector2:
        '''앵커를 계산한 렌더 위치'''
        return self.pos - self.size.elementwise() * self.anchor

    @property
    def rect(self) -> pg.Rect:
        '''스크린상 클릭 판정용 사각형'''
        return pg.Rect(self.screen_pos, self.size)

    @property
    def is_hovered(self) -> bool:
        '''마우스가 버튼 위에 있는가?'''
        mouse_pos = pg.Vector2(pg.mouse.get_pos())
        return self.rect.collidepoint(mouse_pos)

    def update(self):
        super().update()

        now_hovered = self.is_hovered
        self.render_image = self.hover_image if now_hovered else self.default_image

        # 호버 관련 애니메이션 & 효과음!!
        if not self._was_hovered and now_hovered:
            self.on_hover(self.name, self, "enter")
            self.app.sound_manager.play_sfx(self.hover_enter_sound)
            Tween(self, "scale", 1, 1.2, .2, tween.easeOutBack)
        elif self._was_hovered and not now_hovered:
            self.on_hover(self.name, self, "exit")
            Tween(self, "scale", 1.2, 1, .2, tween.easeInBack)
            self.app.sound_manager.play_sfx(self.hover_exit_sound)

        # 클릭 처리
        for event in self.app.events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == self.button and now_hovered:
                self.app.sound_manager.play_sfx(self.click_sound)
                self.on_click(self.name, self)

        # 상태 업데이트
        self._was_hovered = now_hovered

    def draw(self):
        super().draw()
        surface = self.app.surfaces[LAYER_INTERFACE]

        scaled_img = pg.transform.scale_by(self.render_image, self.scale)
        surface.blit(scaled_img, self.screen_pos)
import pygame as pg

from scripts.constants import *
from scripts.objects import *

class ImageButton(GameObject):
    '''action 형식: def action(name: str, button: ImageButton): ...'''
    '''스크린 기준 UI 버튼'''

    def __init__(self, 
                 name: str, 
                 position: pg.Vector2, 
                 action: callable,
                 button: int = 1,
                 anchor: pg.Vector2 = pg.Vector2(0, 0)):
        super().__init__()
        self.name = name
        self.pos = position
        self.action = action
        self.button = button  # 1=좌클릭, 2=휠, 3=우클릭
        self.anchor = anchor  # (0,0)=좌상단, (0.5,0.5)=중앙, (1,1)=우하단

        self.hover_image = self.app.ASSETS["ui"]["image_button"][name]["on_hover"]
        self.default_image = self.app.ASSETS["ui"]["image_button"][name]["on_not_hover"]
        self.render_image = self.default_image

    @property
    def size(self) -> pg.Vector2:
        return pg.Vector2(self.render_image.get_size())

    @property
    def screen_pos(self) -> pg.Vector2:
        return self.pos - self.size.elementwise() * self.anchor

    @property
    def rect(self) -> pg.Rect:
        return pg.Rect(self.screen_pos, self.size)

    def update(self):
        super().update()
        mouse_pos = pg.Vector2(pg.mouse.get_pos())
        is_hovered = self.rect.collidepoint(mouse_pos)

        self.render_image = self.hover_image if is_hovered else self.default_image

        for event in self.app.events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == self.button and is_hovered:
                self.action(self.name, self)

    def draw(self):
        super().draw()
        surface = self.app.surfaces[LAYER_INTERFACE]
        surface.blit(self.render_image, self.screen_pos)
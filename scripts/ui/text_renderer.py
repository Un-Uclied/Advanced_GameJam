import pygame as pg

from scripts.constants import *
from scripts.objects import *

BASE_FONT_PATH = "assets/fonts/"

class TextRenderer(GameObject):
    '''텍스트, 위치, 색상은 런타임중 바꿀수 있으나, 폰트와 크기는 변경 불가 (성능상의 이유로)'''
    '''pygame.freetype은 성능을 많이 잡아먹어서 pg.font.Font를 사용'''
    '''ui는 스크린 위치 사용'''
    def __init__(self, 
                 start_text : str,
                 pos: pg.Vector2,
                 font_name : str = "default",
                 font_size: int = 24,
                 color: pg.Color = pg.Color(255, 255, 255)):
        super().__init__()

        self.text = start_text
        self.pos = pos
        self.color = color

        #self.app.ASSETS["fonts"][font_name]에는 폰트 파일의 이름만 들어있고, pg.font.Font 생성은 여기서 생성.
        self.font = pg.font.Font(BASE_FONT_PATH + self.app.ASSETS["fonts"][font_name], font_size)

    def draw(self):
        super().draw()
        surface = self.app.surfaces[LAYER_INTERFACE]
        
        text_surf = self.font.render(self.text, False, self.color)
        surface.blit(text_surf, self.pos)
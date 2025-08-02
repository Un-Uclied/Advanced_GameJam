import pygame as pg
import pytweening as tween

from scripts.constants import *
from .tween import Tween

from scripts.objects import GameObject
class ScreenFader(GameObject):
    '''
    App에서 부르는 페이드 이펙트
    
    :param duration: 걸리는 시간
    :param fade_in: True면 투명에서 검정으로, False면 검정에서 투명으로
    :param on_complete: 끝났을때 할꺼 함수
    '''

    def __init__(self, duration : float, fade_in : bool, on_complete):
        super().__init__()
        self.surface = pg.Surface(SCREEN_SIZE, pg.SRCALPHA)
        self.surface.fill((0, 0, 0))
        self.surface.set_alpha(0 if fade_in else 255)

        self.alpha = 0 if fade_in else 255
        self.fade_in = fade_in
        self.on_complete = on_complete

        # 트윈 추가
        Tween(self, "alpha", self.alpha, 255 if fade_in else 0, duration, tween.easeInCubic).on_complete.append(self.fade_done)

    def fade_done(self):
        if self.on_complete is not None:
            self.on_complete()
        self.destroy()

    def draw(self):
        self.surface.set_alpha(int(self.alpha))
        self.app.surfaces[LAYER_INTERFACE].blit(self.surface, (0, 0))
import pygame as pg
import pytweening as pt

from scripts.constants import *
from scripts.core import *

class ScreenFader(GameObject):
    """
    화면 전체를 검정으로 페이드 인/아웃하는 UI 효과.

    사용법:
    - App에서 씬 전환할 때, 화면 전환 효과로 쓰임.
    - duration 초 동안 alpha를 0~255 또는 255~0으로 부드럽게 변화시킴.
    - 페이드 완료 후 콜백 함수 실행 가능.

    :param duration: 페이드 진행 시간(초)
    :param fade_in: True면 투명 → 검정 (화면 어두워짐)
                    False면 검정 → 투명 (화면 밝아짐)
    :param on_complete: 페이드 완료 시 호출할 함수 (옵션)
    """

    def __init__(self, duration : float, fade_in : bool, on_complete = None):
        super().__init__()

        # 전체 화면 덮을 투명 검정 Surface 생성
        self.surface = pg.Surface(SCREEN_SIZE, pg.SRCALPHA)
        self.surface.fill((0, 0, 0))

        # 초기 알파 값 세팅 (페이드 방향에 따라 0 or 255)
        self.alpha = 0 if fade_in else 255
        self.surface.set_alpha(self.alpha)

        self.fade_in = fade_in
        self.on_complete = on_complete

        # Tween으로 alpha를 목표값까지 자연스럽게 변화시킴
        target_alpha = 255 if fade_in else 0
        Tween(self, "alpha", self.alpha, target_alpha, duration, pt.easeInCubic, use_unscaled_time=True)\
            .on_complete.append(self.fade_done)

    def fade_done(self):
        # 페이드 완료 후 콜백 실행 및 객체 제거
        if self.on_complete is not None:
            self.on_complete()
        self.destroy()

    def draw(self):
        # 매 프레임 alpha 업데이트하고 화면에 덮음
        self.surface.set_alpha(int(self.alpha))
        self.app.surfaces[LAYER_INTERFACE].blit(self.surface, (0, 0))
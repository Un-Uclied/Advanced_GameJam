import pygame as pg

from scripts.constants import *
from scripts.core import *
from .text_renderer import TextRenderer

class PopupText(TextRenderer):
    """
    팝업으로 잠깐 뜨는 텍스트 (딜레이 후 페이드 아웃 & 자동 삭제)

    Args:
        text (str): 출력할 텍스트
        position (pg.Vector2): 위치
        fade_delay (float): 페이드 시작 전 대기 시간 (초)
        fade_duration (float): 페이드 아웃 지속 시간 (초)
        font_name (str): 폰트 이름
        font_size (int): 폰트 크기
        color (pg.Color): 텍스트 색상
        anchor (pg.Vector2): 앵커 (기본 중앙)
        use_camera (bool): 카메라 적용 여부
    """
    def __init__(self, text: str, position: pg.Vector2,
                 fade_delay: float = 1.0, fade_duration: float = 2.5,
                 font_name: str = "default", font_size: int = 24,
                 color: pg.Color = pg.Color("white"),
                 anchor: pg.Vector2 = pg.Vector2(0.5, 0.5), use_camera: bool = False):
        super().__init__(text, position, font_name, font_size, color, anchor, use_camera)

        self.fade_duration = fade_duration
        # 딜레이 후 페이드 아웃 시작
        Timer(fade_delay, on_time_out=self._start_fade, auto_destroy=True, use_unscaled=True)

    def _start_fade(self):
        # 알파값 255 -> 0으로 Tween, 끝나면 자기 자신 파괴
        tween = Tween(self, "alpha", 255, 0, self.fade_duration, use_unscaled_time=True)
        tween.on_complete.append(self.destroy)
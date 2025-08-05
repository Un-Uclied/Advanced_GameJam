import pygame as pg

from scripts.constants import *
from scripts.core import *
from .text_renderer import TextRenderer

class PopupText(TextRenderer):
    def __init__(self, text, position,
                 fade_delay = 1, fade_duration = 2.5,
                 font_name = "default", font_size = 24,
                 color = pg.Color("white"),
                 anchor = pg.Vector2(.5, .5), use_camera = False):
        super().__init__(text, position, font_name, font_size, color, anchor, use_camera)

        self.fade_dur = fade_duration
        Timer(fade_delay, on_time_out=self.on_delay_end, auto_destroy=True, use_unscaled=True)

    def on_delay_end(self):
        # 트윈 시작, 끝나면 지우기
        Tween(self, "alpha", 255, 0, self.fade_dur, use_unscaled_time=True).on_complete.append(
            lambda: self.destroy()
        )
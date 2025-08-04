import pygame as pg
import webbrowser

from scripts.constants import *
from scripts.backgrounds import *
from scripts.ui import *
from .base import Scene

def on_github_button_click(button : TextButton):
    webbrowser.open("https://github.com/Un-Uclied/Advanced_GameJam")

class InfoScene(Scene):
    def on_scene_start(self):
        TextRenderer("[ESC]", pg.Vector2(10, 10), font_name="bold", font_size=20, anchor=pg.Vector2(0, 0))
        TextRenderer("팀 [후라이맨즈]", pg.Vector2(SCREEN_SIZE.x / 2, 150), font_name="bold", font_size=100, anchor=pg.Vector2(0.5, 0.5))
        TextRenderer("<팀원>", pg.Vector2(SCREEN_SIZE.x / 2, 250), anchor=pg.Vector2(0.5, 0.5))
        TextRenderer("서준범 (팀장)", pg.Vector2(SCREEN_SIZE.x / 2, 320), anchor=pg.Vector2(0.5, 0.5))
        TextRenderer("심규원", pg.Vector2(SCREEN_SIZE.x / 2, 370), anchor=pg.Vector2(0.5, 0.5))
        TextRenderer("이준영", pg.Vector2(SCREEN_SIZE.x / 2, 420), anchor=pg.Vector2(0.5, 0.5))
        TextButton("[github 페이지 바로 가기]", pg.Vector2(SCREEN_SIZE.x / 2, SCREEN_SIZE.y - 50), on_github_button_click, None, font_size = 48)
        super().on_scene_start()
        
        Sky()

    def update(self):
        super().update()
        for event in self.app.events:
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.app.change_scene("main_menu_scene")
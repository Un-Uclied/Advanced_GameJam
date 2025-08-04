import pygame as pg

from scripts.constants import *
from scripts.backgrounds import *
from scripts.ui import *
from scripts.core import *
from scripts.volume import *
from scripts.tilemap import *
from .base import Scene

class MainMenuScene(Scene):
    def on_scene_start(self):
        self.tilemap = Tilemap("main_menu.json")
        spawn_all_entities(self.tilemap)

        ImageButton("game_start", pg.Vector2(SCREEN_SIZE.x / 2, 400), self.on_click, None)
        ImageButton("app_settings", pg.Vector2(SCREEN_SIZE.x / 2, 500), self.on_click, None)
        ImageButton("app_info", pg.Vector2(SCREEN_SIZE.x / 2, 600), self.on_click, None)
        ImageButton("app_quit", pg.Vector2(SCREEN_SIZE.x / 2, 700), self.on_click, None)
        ImageRenderer(self.app.ASSETS["ui"]["vignette"]["black"], pg.Vector2(0, 0), anchor=pg.Vector2(0, 0))
        TextRenderer("< Limen >", pg.Vector2(SCREEN_SIZE.x / 2, 150), font_name="gothic", font_size=170, anchor=pg.Vector2(0.5, 0.5))
        TextRenderer("팀 후라이맨즈", SCREEN_SIZE - pg.Vector2(25, 25), anchor=pg.Vector2(1, 1))

        super().on_scene_start()
        # 엔티티들이 움직이는 속도가 너무 빨라서 느리게 하기
        self.app.time_scale = .5

        Sky()
        Clouds()
        Fog()

    def on_click(self, button : ImageButton):
        name = button.name

        if name == "game_start":
            self.app.change_scene("chapter_select_scene")
        if name == "app_settings":
            self.app.change_scene("settings_scene")
        if name == "app_info":
            self.app.change_scene("info_scene")
        if name == "app_quit":
            self.app.window_should_be_closed = True

        # 그저 타격감을 위한 효과
        self.app.scene.camera.shake_amount += 15

    def on_scene_end(self):
        # 끝날때 원상복구
        self.app.time_scale = 1.0
        super().on_scene_end()
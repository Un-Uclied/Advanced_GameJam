import pygame as pg

from scripts.constants import *
from scripts.backgrounds import *
from scripts.ui import *
from scripts.core import *
from scripts.volume import *
from scripts.tilemap import *
from .base import Scene

def on_click(name : str, button : ImageButton):
    from scripts.app import App
    app = App.singleton

    if name == "game_start":
        app.change_scene("main_game_scene")
    if name == "app_settings":
        app.change_scene("settings_scene")
    if name == "app_info":
        app.change_scene("info_scene")
    if name == "app_quit":
        app.window_should_be_closed = True

    # 그저 타격감을 위한 효과
    app.scene.camera.shake_amount += 15

class MainMenuScene(Scene):
    def on_scene_start(self):
        self.tilemap = Tilemap("main_menu.json")
        spawn_all_entities(self.tilemap)

        ImageButton("game_start", pg.Vector2(SCREEN_SIZE.x / 2, 400), on_click, None)
        ImageButton("app_settings", pg.Vector2(SCREEN_SIZE.x / 2, 500), on_click, None)
        ImageButton("app_info", pg.Vector2(SCREEN_SIZE.x / 2, 600), on_click, None)
        ImageButton("app_quit", pg.Vector2(SCREEN_SIZE.x / 2, 700), on_click, None)
        ImageRenderer(self.app.ASSETS["ui"]["vignette"]["black"], pg.Vector2(0, 0), anchor=pg.Vector2(0, 0))
        TextRenderer("< Limen >", pg.Vector2(SCREEN_SIZE.x / 2, 150), font_name="gothic", font_size=170, anchor=pg.Vector2(0.5, 0.5))

        super().on_scene_start()
        self.app.time_scale = .5

        Sky()
        Clouds()
        Fog()

    def on_scene_end(self):
        super().on_scene_end()
        self.app.time_scale = 1.0
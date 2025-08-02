import pygame as pg

from scripts.constants import *
from scripts.backgrounds import *
from scripts.ui import *
from scripts.core import *
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

def on_hover(name : str, button : ImageButton, status : str):
    if name == "game_start" and status == "enter":
        text = TextRenderer("게임 시작 !!!!", pg.Vector2(400, 500))
        Tween(text, "alpha", 255, 0, 2).on_complete.append(lambda: text.destroy())

class MainMenuScene(Scene):
    def on_scene_start(self):
        super().on_scene_start()
        Sky()

        ImageButton("game_start", pg.Vector2(SCREEN_SIZE.x / 2, 400), on_click, on_hover, anchor=pg.Vector2(.5, .5))
        ImageButton("app_settings", pg.Vector2(SCREEN_SIZE.x / 2, 500), on_click, on_hover, anchor=pg.Vector2(.5, .5))
        ImageButton("app_info", pg.Vector2(SCREEN_SIZE.x / 2, 600), on_click, on_hover, anchor=pg.Vector2(.5, .5))
        ImageButton("app_quit", pg.Vector2(SCREEN_SIZE.x / 2, 700), on_click, on_hover, anchor=pg.Vector2(.5, .5))
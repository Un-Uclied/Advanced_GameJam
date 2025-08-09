import pygame as pg
import json
import random

from scripts.constants import *
from scripts.backgrounds import *
from scripts.ui import *
from scripts.core import *
from scripts.volume import *
from scripts.tilemap import *
from .base import Scene

with open("data/tilemap_data.json", encoding="utf-8") as f:
    TILEMAP_DATA = json.load(f)

class MainMenuUI:
    """메인 메뉴 화면의 모든 UI 요소를 관리하는 클래스"""
    def __init__(self, scene):
        self.scene = scene
        self._buttons : list[ImageButton] = []
        self._create_ui_elements()
        self._connect_events()

    def _create_ui_elements(self):
        """UI 요소 생성 및 초기 설정"""
        self._buttons.extend(
        [
            ImageButton("game_start", pg.Vector2(SCREEN_SIZE.x / 2, 400), None, None),
            ImageButton("app_settings", pg.Vector2(SCREEN_SIZE.x / 2, 500), None, None),
            ImageButton("app_info", pg.Vector2(SCREEN_SIZE.x / 2, 600), None, None),
            ImageButton("app_quit", pg.Vector2(SCREEN_SIZE.x / 2, 700), None, None),
            ImageRenderer(self.scene.app.ASSETS["ui"]["vignette"]["black"], pg.Vector2(0, 0), anchor=pg.Vector2(0, 0))
        ]
        )
        
        TextRenderer("< Limen >", pg.Vector2(SCREEN_SIZE.x / 2, 150), font_name="gothic", font_size=170, anchor=pg.Vector2(0.5, 0.5))
        TextRenderer("팀 후라이맨즈", SCREEN_SIZE - pg.Vector2(25, 25), anchor=pg.Vector2(1, 1))

    def _connect_events(self):
        """UI 요소에 이벤트 핸들러 연결"""
        # 버튼에 on_click 핸들러를 연결
        for ui_element in self._buttons:
            ui_element.on_click = self.on_click

    def on_click(self, button: ImageButton):
        """버튼 클릭 시 해당 씬으로 이동"""
        name = button.name
        app = self.scene.app

        if name == "game_start":
            app.change_scene("chapter_select_scene")
        elif name == "app_settings":
            app.change_scene("settings_scene")
        elif name == "app_info":
            app.change_scene("info_scene")
        elif name == "app_quit":
            app.window_should_be_closed = True

        # 타격감을 위한 화면 흔들림 효과
        app.scene.camera.shake_amount += 15

class MainMenuScene(Scene):
    """메인 메뉴 씬 클래스. 게임 시작, 설정 등 주요 메뉴를 관리"""
    def __init__(self):
        super().__init__()
        self.main_menu_ui = None

    def on_scene_start(self):
        """씬 시작 시 타일맵, 배경, UI를 초기화"""
        super().on_scene_start()        

        self.tilemap = Tilemap(random.choice(TILEMAP_DATA["main_menu_maps"]))
        spawn_all_entities(self.tilemap)

        self.main_menu_ui = MainMenuUI(self)

        Sky()
        Clouds()
        Fog()
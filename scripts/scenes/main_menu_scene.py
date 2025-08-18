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

# 메인 메뉴용 타일맵 데이터 JSON 미리 로드 (한 번만)
with open("data/tilemap_data.json", encoding="utf-8") as f:
    TILEMAP_DATA = json.load(f)

class MainMenuUI:
    """
    메인 메뉴의 UI 전담 클래스
    - 여러 버튼들 (시작, 설정, 정보, 종료)
    - 배경 비네팅 이미지
    - 타이틀, 팀명 텍스트

    :param scene: 이 UI가 속한 씬 (MainMenuScene 인스턴스)
    """
    def __init__(self, scene):
        self.scene = scene
        self._buttons : list[ImageButton] = []
        self._make_ui()
        self._connect_events()

    def _make_ui(self):
        """UI 컴포넌트 생성 및 화면 위치 세팅"""
        # 버튼들 생성, 화면 가운데 수평 정렬, Y 좌표만 다름
        self._buttons.extend(
            [
                ImageButton("game_start", pg.Vector2(SCREEN_SIZE.x / 2, 400), None, None),
                ImageButton("app_settings", pg.Vector2(SCREEN_SIZE.x / 2, 500), None, None),
                ImageButton("app_info", pg.Vector2(SCREEN_SIZE.x / 2, 600), None, None),
                ImageButton("app_quit", pg.Vector2(SCREEN_SIZE.x / 2, 700), None, None),
                # 화면 전체 덮는 검은 비네팅 이미지 (앵커 좌상단 고정)
                ImageRenderer(self.scene.app.ASSETS["ui"]["vignette"]["black"], pg.Vector2(0, 0), anchor=pg.Vector2(0, 0))
            ]
        )
        # 타이틀 텍스트 & 팀명 텍스트 생성
        TextRenderer(
            "< Limen >", pg.Vector2(SCREEN_SIZE.x / 2, 150),
            font_name="gothic", font_size=170, anchor=pg.Vector2(0.5, 0.5)
        )
        TextRenderer(
            "팀 후라이맨즈",
            SCREEN_SIZE - pg.Vector2(25, 25),
            anchor=pg.Vector2(1, 1)
        )

    def _connect_events(self):
        """각 버튼에 클릭 이벤트 함수 연결"""
        for ui_element in self._buttons:
            ui_element.on_click = self.on_click

    def on_click(self, button: ImageButton):
        """버튼 클릭 시 동작 분기 처리"""
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

        # 버튼 클릭 시 약간의 화면 흔들림 효과로 타격감 추가
        app.scene.camera.shake_amount += 15

class MainMenuScene(Scene):
    """
    메인 메뉴 씬 클래스

    씬 시작 시:
    - 랜덤 메인 메뉴용 타일맵 로드 및 엔티티 생성
    - 하늘, 구름, 안개 효과 생성
    - 메인 메뉴 UI 생성
    """
    def __init__(self):
        super().__init__()
        self.main_menu_ui = None

    def on_scene_start(self):
        super().on_scene_start()

        # 랜덤으로 메인 메뉴용 타일맵 불러와 씬에 생성
        self.tilemap_data = TilemapData(random.choice(TILEMAP_DATA["main_menu_maps"]))
        TilemapRenderer(self.tilemap_data)
        spawn_all_entities_by_data(self.tilemap_data)

        # UI 생성
        self.main_menu_ui = MainMenuUI(self)

        # 브금
        self.app.sound_manager.play_bgm("main_menu")

        # 배경 이펙트 생성
        Sky()
        Clouds()
        Fog()
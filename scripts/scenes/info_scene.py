import pygame as pg
import webbrowser

from scripts.constants import *
from scripts.backgrounds import *
from scripts.ui import *
from .base import Scene

ASSET_LINKS = [
    "https://cainos.itch.io/pixel-art-platformer-village-props",
    "https://xyezawr.itch.io/free",
    "https://bdragon1727.itch.io/1050-rpg-effects-64x64",
    "https://xyezawr.itch.io/gif-free-pixel-effects-pack-5-blood-effects",
    "https://xyezawr.itch.io/free-pixel-effects-pack-4-explosions",
    "https://szadiart.itch.io/pixel-fantasy-caves",
    "https://corwin-zx.itch.io/the-pale-moonlight",
    "https://free-game-assets.itch.io/free-moon-pixel-game-backgrounds",
    "https://ragnapixel.itch.io/particle-fx",
    "https://www.youtube.com/watch?v=whLbGbpt-E4&t=1s",
    "https://codemanu.itch.io/pixelart-effect-pack"
]

class InfoUI:
    """정보 화면의 모든 UI 요소를 관리하는 클래스"""
    def __init__(self, scene):
        self.scene = scene
        self._create_ui_elements()
        self._connect_events()

    def _create_ui_elements(self):
        """UI 요소 생성 및 초기 설정"""
        TextRenderer("[ESC]", pg.Vector2(10, 10), font_name="bold", font_size=20, anchor=pg.Vector2(0, 0))
        TextRenderer("팀 [후라이맨즈]", pg.Vector2(SCREEN_SIZE.x / 2, 100), font_name="bold", font_size=100, anchor=pg.Vector2(0.5, 0.5))
        TextRenderer("<팀원>", pg.Vector2(SCREEN_SIZE.x / 2, 200), anchor=pg.Vector2(0.5, 0.5))
        TextRenderer("서준범 (팀장)", pg.Vector2(SCREEN_SIZE.x / 2, 250), anchor=pg.Vector2(0.5, 0.5))
        TextRenderer("심규원", pg.Vector2(SCREEN_SIZE.x / 2, 280), anchor=pg.Vector2(0.5, 0.5))
        TextRenderer("이준영", pg.Vector2(SCREEN_SIZE.x / 2, 310), anchor=pg.Vector2(0.5, 0.5))
        self.github_button = TextButton("[github 페이지 바로 가기]", pg.Vector2(SCREEN_SIZE.x / 2, 370), None, None, font_size=48)
        TextRenderer("사용된 무료 에셋", pg.Vector2(SCREEN_SIZE.x / 2, 450), font_name="bold", font_size=60, anchor=pg.Vector2(0.5, 0.5))
        for i, link in enumerate(ASSET_LINKS):
            TextRenderer(link, pg.Vector2(SCREEN_SIZE.x / 2, 500 + i * 30), font_size=15, anchor=pg.Vector2(0.5, 0.5))

    def _connect_events(self):
        """UI 요소에 이벤트 핸들러 연결"""
        self.github_button.on_click = self.on_github_button_click

    def on_github_button_click(self, button: TextButton):
        """깃허브 버튼 클릭 시 웹 브라우저 열기"""
        webbrowser.open("https://github.com/Un-Uclied/Advanced_GameJam")

class InfoScene(Scene):
    """정보 씬 클래스. 팀 정보와 GitHub 링크를 표시"""
    def __init__(self):
        super().__init__()
        self.info_ui = None

    def on_scene_start(self):
        """씬 시작 시 UI와 배경 초기화"""
        self.info_ui = InfoUI(self)
        super().on_scene_start()
        
        Sky()
    
    def update(self):
        """매 프레임마다 호출"""
        super().update()
        for event in self.app.events:
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.app.change_scene("main_menu_scene")
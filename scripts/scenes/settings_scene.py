import pygame as pg

from scripts.constants import *
from scripts.backgrounds import Sky
from scripts.ui import *
from .base import Scene

# 모든 데이터 초기화 버튼 누를 때마다 보여줄 메시지
RESET_MSGS = [
    "모든 진행 상황과 설정이 초기화됩니다. 그래도 계속하시겠습니까?",
    "진짜 정말로 계속하시겠습니까?",
    "후회 안하시겠습니까?",
    "진짜 정말로 후회 안하시겠습니까?",
    "제가 보기엔 후회할거 같습니다..;",
    "그래도 진짜 하겠습니까?",
    "그럼 진짜 초기화 하겠습니다.",
    "이번엔 진짜 마지막으로 계속하시겠습니까?"
]

class SettingsUI:
    """설정 화면의 모든 UI 요소를 관리하는 클래스"""
    def __init__(self, scene):
        self.scene = scene
        self.button_click_stack = 0
        self.sfx_volume_text = None
        self.bgm_volume_text = None
        self.sfx_volume_slider = None
        self.bgm_volume_slider = None
        self.reset_button = None
        
        self._create_ui_elements()
        self._connect_events()

    def _create_ui_elements(self):
        """UI 요소 생성 및 초기 설정"""
        TextRenderer("[ESC]", pg.Vector2(10, 10), font_name="bold", font_size=20, anchor=pg.Vector2(0, 0))
        TextRenderer("설정", pg.Vector2(SCREEN_SIZE.x / 2, 150), font_name="bold", font_size=100, anchor=pg.Vector2(0.5, 0.5))

        self.sfx_volume_slider = Slider(pg.Vector2(SCREEN_SIZE.x / 2, 400), pg.Vector2(450, 50), self.scene.app.player_data["vfx_volume"], 0, 1)
        self.sfx_volume_text = TextRenderer(str(self.scene.app.player_data["vfx_volume"]), pg.Vector2(SCREEN_SIZE.x / 2 - 250, 400), anchor=pg.Vector2(1, .5))

        self.bgm_volume_slider = Slider(pg.Vector2(SCREEN_SIZE.x / 2, 480), pg.Vector2(450, 50), self.scene.app.player_data["bgm_volume"], 0, 1)
        self.bgm_volume_text = TextRenderer(str(self.scene.app.player_data["bgm_volume"]), pg.Vector2(SCREEN_SIZE.x / 2 - 250, 480), anchor=pg.Vector2(1, .5))

        self.reset_button = TextButton("모든 데이터 초기화", pg.Vector2(SCREEN_SIZE.x / 2, 700), None, font_size=28, hover_color=pg.Color("yellow"), not_hover_color=pg.Color("red"))

    def _connect_events(self):
        """UI 요소에 이벤트 핸들러 연결"""
        self.sfx_volume_slider.on_change = self.change_vfx
        self.bgm_volume_slider.on_change = self.change_bgm
        self.reset_button.on_click = self.on_reset_button_click

    def on_reset_button_click(self, button: TextButton):
        """리셋 버튼 클릭 시 여러 단계에 걸쳐 초기화 확인"""
        if self.button_click_stack >= len(RESET_MSGS):
            self.scene.app.reset_player_data()
            self.reset_button.renderer.text = "모든 데이터 초기화 됨."

            self.sfx_volume_slider.update_rects()
            self.bgm_volume_slider.update_rects()

            self.scene.app.sound_manager.play_sfx(self.scene.app.ASSETS["sounds"]["ui"]["reset"])

            self.scene.app.change_scene("main_menu_scene")
        else:
            self.reset_button.renderer.text = RESET_MSGS[self.button_click_stack]
        self.button_click_stack += 1

    def update_texts(self):
        """슬라이더 값에 따라 텍스트 업데이트"""
        self.sfx_volume_text.text = "SFX 음량 : " + str(self.scene.app.player_data["vfx_volume"])
        self.bgm_volume_text.text = "BGM 음량 : " + str(self.scene.app.player_data["bgm_volume"])

    def change_vfx(self):
        """SFX 볼륨 변경"""
        self.scene.app.player_data["vfx_volume"] = round(self.sfx_volume_slider.value, 2)

    def change_bgm(self):
        """BGM 볼륨 변경"""
        self.scene.app.player_data["bgm_volume"] = round(self.bgm_volume_slider.value, 2)

class SettingsScene(Scene):
    """설정 씬 클래스"""
    def __init__(self):
        super().__init__()
        self.settings_ui = None

    def on_scene_start(self):
        """씬 시작 시 UI와 배경 초기화"""
        self.settings_ui = SettingsUI(self)
        super().on_scene_start()
        
        Sky()

    def on_scene_end(self):
        """씬 종료 시 변경된 설정 저장"""
        self.app.save_player_data()
        super().on_scene_end()

    def handle_input(self):
        """입력 처리 (ESC 키로 메인 메뉴 이동)"""
        for event in self.app.events:
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.app.change_scene("main_menu_scene")
    
    def update(self):
        """매 프레임마다 호출"""
        super().update()
        self.handle_input()
        self.settings_ui.update_texts()
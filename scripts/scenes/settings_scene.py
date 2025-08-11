import pygame as pg
from scripts.constants import *
from scripts.backgrounds import Sky
from scripts.ui import *
from .base import Scene

# 모든 데이터 초기화 버튼 클릭 시 표시될 메시지 리스트
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
    """
    설정 화면의 모든 UI 요소를 관리하는 클래스.
    """
    def __init__(self, scene):
        self.scene = scene
        self.button_click_stack = 0
        self.ui_elements = {}  # 만든 UI 저장
        self._init_ui()
        self._connect_events()

    def _init_ui(self):
        """UI 요소 생성 (동적 생성 꼼수)"""
        # 텍스트 요소
        for text, pos, kwargs in [
            ("[ESC]", (10, 10), dict(font_name="bold", font_size=20, anchor=pg.Vector2(0, 0))),
            ("설정", (SCREEN_SIZE.x / 2, 150), dict(font_name="bold", font_size=100, anchor=pg.Vector2(0.5, 0.5))),
        ]:
            TextRenderer(text, pg.Vector2(*pos), **kwargs)

        # 슬라이더 데이터 (이름, 초기값 키, y좌표)
        sliders = [
            ("sfx_volume", "vfx_volume", 400),
            ("bgm_volume", "bgm_volume", 480),
        ]

        for name, key, y in sliders:
            self.ui_elements[f"{name}_slider"] = Slider(
                pg.Vector2(SCREEN_SIZE.x / 2, y), pg.Vector2(450, 50),
                self.scene.app.player_data[key], 0, 1
            )
            self.ui_elements[f"{name}_text"] = TextRenderer(
                str(self.scene.app.player_data[key]),
                pg.Vector2(SCREEN_SIZE.x / 2 - 250, y), anchor=pg.Vector2(1, .5)
            )

        # 버튼 데이터 (이름, 표시 텍스트, y좌표, hover색, 기본색)
        buttons = [
            ("reset_button", "모든 데이터 초기화", 650, pg.Color("yellow"), pg.Color("red")),
            ("unlock_button", "모든 레벨 잠금 해제", 700, pg.Color("blue"), pg.Color("red")),
        ]

        for name, text, y, hover, normal in buttons:
            self.ui_elements[name] = TextButton(
                text, pg.Vector2(SCREEN_SIZE.x / 2, y), None, font_size=28,
                hover_color=hover, not_hover_color=normal
            )

        # ui_elements를 멤버 변수로 꺼내 쓰기
        globals().update(self.ui_elements)

    def _connect_events(self):
        """이벤트 연결"""
        self.ui_elements["sfx_volume_slider"].on_value_changed = self.change_vfx
        self.ui_elements["bgm_volume_slider"].on_value_changed = self.change_bgm
        self.ui_elements["reset_button"].on_click = self.on_reset_button_click
        self.ui_elements["unlock_button"].on_click = self.on_unlock_button_click

    def update_texts(self):
        """볼륨 표시 업데이트"""
        self.ui_elements["sfx_volume_text"].text = f"SFX 음량 : {self.scene.app.player_data['vfx_volume']}"
        self.ui_elements["bgm_volume_text"].text = f"BGM 음량 : {self.scene.app.player_data['bgm_volume']}"

    def change_vfx(self):
        self.scene.app.player_data["vfx_volume"] = round(self.ui_elements["sfx_volume_slider"].value, 2)

    def change_bgm(self):
        self.scene.app.player_data["bgm_volume"] = round(self.ui_elements["bgm_volume_slider"].value, 2)

    def on_reset_button_click(self, _):
        if self.button_click_stack >= len(RESET_MSGS):
            self.scene.app.reset_player_data()
            self.ui_elements["reset_button"].renderer.text = "모든 데이터 초기화 됨."
            self.ui_elements["sfx_volume_slider"].update_rects()
            self.ui_elements["bgm_volume_slider"].update_rects()
            self.scene.app.sound_manager.play_sfx(self.scene.app.ASSETS["sounds"]["ui"]["reset"])
            self.scene.app.change_scene("main_menu_scene")
        else:
            self.ui_elements["reset_button"].renderer.text = RESET_MSGS[self.button_click_stack]
        self.button_click_stack += 1

    def on_unlock_button_click(self, _):
        self.scene.app.player_data["progress"] = {
            "1": [True] * 5,
            "2": [True] * 5,
            "3": [True] * 5,
            "4": [True]
        }
        self.ui_elements["unlock_button"].renderer.text = "모든 레벨 잠금 해제 됨."
        self.scene.app.sound_manager.play_sfx(self.scene.app.ASSETS["sounds"]["ui"]["unlock"])
        self.scene.app.save_player_data()
        self.scene.app.change_scene("main_menu_scene")


class SettingsScene(Scene):
    """
    설정 화면 씬.
    - UI 생성 및 관리
    - 설정 변경 저장
    """
    def __init__(self):
        super().__init__()
        self.settings_ui = None

    def on_scene_start(self):
        """씬 시작 시 UI 및 배경 초기화"""
        self.settings_ui = SettingsUI(self)
        super().on_scene_start()
        Sky()

    def on_scene_end(self):
        """씬 종료 시 변경 사항 저장"""
        self.app.save_player_data()
        super().on_scene_end()

    def handle_input(self):
        """ESC 키 입력 시 메인 메뉴로 이동"""
        for event in self.app.events:
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.app.change_scene("main_menu_scene")

    def update(self):
        """프레임 업데이트"""
        super().update()
        self.handle_input()
        self.settings_ui.update_texts()
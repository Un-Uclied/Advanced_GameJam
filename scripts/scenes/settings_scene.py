import pygame as pg

from scripts.constants import *
from scripts.backgrounds import Sky
from scripts.ui import *
from .base import Scene

RESET_MSGS = [
    "모든 진행 상황과 설정이 초기화 됩니다. 그래도 계속하시겠습니까?",
    "진짜 정말로 계속하시겠습니까?",
    "후회 안하시겠습니까?",
    "진짜 정말로 후회 안하시겠습니까?",
    "제가 보기엔 후회할거 같습니다..;",
    "그래도 진짜 하겠습니까?",
    "그럼 진짜 초기화 하겠습니다.",
    "이번엔 진짜 마지막으로 계속하시겠습니까?"
]

class SettingsScene(Scene):
    def on_scene_start(self):
        TextRenderer("[ESC]", pg.Vector2(10, 10), font_name="bold", font_size=20, anchor=pg.Vector2(0, 0))
        TextRenderer("설정", pg.Vector2(SCREEN_SIZE.x / 2, 150), font_name="bold", font_size=100, anchor=pg.Vector2(0.5, 0.5))
        self.sfx_volume_slider = Slider(pg.Vector2(SCREEN_SIZE.x / 2, 400), pg.Vector2(450, 50), self.app.player_data["vfx_volume"], 0, 1, self.change_vfx)
        self.sfx_volume_text = TextRenderer(str(self.app.player_data["vfx_volume"]), pg.Vector2(SCREEN_SIZE.x / 2 - 250, 400), anchor=pg.Vector2(1, .5))

        self.bgm_volume_slider = Slider(pg.Vector2(SCREEN_SIZE.x / 2, 480), pg.Vector2(450, 50), self.app.player_data["bgm_volume"], 0, 1, self.change_bgm)
        self.bgm_volume_text = TextRenderer(str(self.app.player_data["bgm_volume"]), pg.Vector2(SCREEN_SIZE.x / 2 - 250, 480), anchor=pg.Vector2(1, .5))

        self.button_click_stack = 0
        self.reset_button = TextButton("모든 데이터 초기화", pg.Vector2(SCREEN_SIZE.x / 2, 700), self.on_reset_button_click, font_size=28, hover_color=pg.Color("yellow"), not_hover_color=pg.Color("red"))

        super().on_scene_start()
        
        Sky()

    def on_reset_button_click(self, button : TextButton):
        if self.button_click_stack >= len(RESET_MSGS):
            self.app.reset_player_data()
            self.reset_button.renderer.text = "모든 데이터 초기화 됨."

            self.sfx_volume_slider.update_rects()
            self.bgm_volume_slider.update_rects()

            self.app.change_scene("main_menu_scene")
        else:
            self.reset_button.renderer.text = RESET_MSGS[self.button_click_stack]
        self.button_click_stack += 1

    def update_texts(self):
        self.sfx_volume_text.text = "SFX 음량 : " + str(self.app.player_data["vfx_volume"])
        self.bgm_volume_text.text = "BGM 음량 : " + str(self.app.player_data["bgm_volume"])

    def change_vfx(self):
        self.app.player_data["vfx_volume"] = round(self.sfx_volume_slider.value, 2)

    def change_bgm(self):
        self.app.player_data["bgm_volume"] = round(self.bgm_volume_slider.value, 2)

    def handle_input(self):
        for event in self.app.events:
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.app.change_scene("main_menu_scene")
    
    def update(self):
        super().update()

        self.handle_input()
        self.update_texts()
    
    def on_scene_end(self):
        # 바꾼거 저장
        self.app.save_player_data()
        super().on_scene_end()
import pygame as pg
import json

from scripts.constants import *
from scripts.backgrounds import *
from scripts.ui import *
from scripts.core import *
from scripts.volume import *
from scripts.tilemap import *
from .base import Scene

with open("data/tilemap_data.json", 'r', encoding="utf-8") as f:
    TILEMAP_DATA = json.load(f)

class ChapterSelectScene(Scene):
    def on_scene_start(self):
        # 타일맵 만들고
        self.tilemap = Tilemap("main_menu.json")
        spawn_all_entities(self.tilemap)
        ImageRenderer(self.app.ASSETS["ui"]["vignette"]["black"], pg.Vector2(0, 0), anchor=pg.Vector2(0, 0))

        TextRenderer("[ESC]", pg.Vector2(10, 10), font_name="bold", font_size=20, anchor=pg.Vector2(0, 0))

        TextRenderer("챕터 선택", pg.Vector2(SCREEN_SIZE.x / 2, 150), font_name="bold", font_size=100, anchor=pg.Vector2(0.5, 0.5))

        # 챕터 선택 버튼
        ImageButton("select_one", pg.Vector2(450, 270), self.on_chapter_click, None)
        ImageButton("select_two", pg.Vector2(570, 270), self.on_chapter_click, None)
        ImageButton("select_three", pg.Vector2(690, 270), self.on_chapter_click, None)
        ImageButton("select_boss", pg.Vector2(810, 270), self.on_chapter_click, None)

        self.selected_chapter = 0
        # 생성된 월드 플레이 버튼
        self.buttons = []

        super().on_scene_start()
        # 엔티티들이 움직이는 속도가 너무 빨라서 느리게 하기
        self.app.time_scale = .5

        Sky()
        Clouds()
        Fog()

    def on_chapter_click(self, button: ImageButton):
        name = button.name

        # 챕터 선택
        if name == "select_one":
            self.selected_chapter = 1
        elif name == "select_two":
            self.selected_chapter = 2
        elif name == "select_three":
            self.selected_chapter = 3
        elif name == "select_boss":
            self.selected_chapter = 4

        # 생성했던 버튼 제거
        for btn in self.buttons:
            btn.destroy()
        self.buttons.clear()

        # 챕터 정보
        chapter_str = str(self.selected_chapter)
        world_names = TILEMAP_DATA["names"][chapter_str]
        progress = self.app.player_data["progress"].get(chapter_str, [])

        # self.app.player_data["progress"][챕터]에서 True인것만 허용
        last_cleared = -1 # 기본은 전부 -1로, 모두 플레이 불가
        for i, cleared in enumerate(progress):
            if cleared: # True또는 False (기본적으로 월드 1-1은 True)
                last_cleared = i
        available_idx = last_cleared

        # 버튼 생성
        for i, name in enumerate(world_names):
            can_play = i <= available_idx

            btn = TextButton(
                f"< {name} >",
                pg.Vector2(200, 400 + i * 60),
                self.on_world_start_click if can_play else self.on_world_blocked_click, # 플레이 가능한것과 아닌건 버튼을 눌렀을때 불리는 메소드가 다름.
                None,
                font_name="bold",
                font_size=32,
                hover_color=pg.Color("blue") if can_play else pg.Color("grey"),      # 플레이 가능한것과 아닌건 색이 다름.
                not_hover_color=pg.Color("white") if can_play else pg.Color("grey"), # 플레이 가능한것과 아닌건 색이 다름.
                anchor=pg.Vector2(0, .5),
                data={"index" : i}
            )
            self.buttons.append(btn)

        # 그저 타격감을 위한 효과
        self.app.scene.camera.shake_amount += 15

    def on_world_start_click(self, button: TextButton):
        '''플레이 가능한 원드 버튼을 눌렀을때 change_scene하기 전에 먼저 플레이할 챕터와 월드 인덱스 설정후, change_scene'''
        self.app.registered_scenes["main_game_scene"].current_chapter = self.selected_chapter
        self.app.registered_scenes["main_game_scene"].current_level = button.data["index"]
        self.app.change_scene("main_game_scene")

    def on_world_blocked_click(self, button: TextButton):
        '''플레이 불가한 월드 버튼을 눌렀을때 플레이 불가 텍스트를 생성후 Tween해서 서서히 없어짐.'''
        txt_renderer = TextRenderer("플레이 불가", pg.Vector2(SCREEN_SIZE.x / 2, 750), anchor=pg.Vector2(.5, .5))
        Tween(txt_renderer, "alpha", 255, 0, .5).on_complete.append(
            lambda: txt_renderer.destroy()
        )

    def handle_input(self):
        for event in self.app.events:
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.app.change_scene("main_menu_scene")

    def update(self):
        super().update()

        self.handle_input()

    def on_scene_end(self):
        # 끝날때 원상복구
        self.app.time_scale = 1.0
        super().on_scene_end()
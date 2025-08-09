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

with open("data/tilemap_data.json", 'r', encoding="utf-8") as f:
    TILEMAP_DATA = json.load(f)

class ChapterSelectScene(Scene):
    def on_scene_start(self):
        super().on_scene_start()
        
        # 타일맵 만들고
        self.tilemap = Tilemap(random.choice(TILEMAP_DATA["main_menu_maps"]))
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
            score = self.app.player_data["scores"][chapter_str][i]
            btn = TextButton(
                f"< {name} > : [ {score} ]",
                pg.Vector2(200, 400 + i * 60),
                # 플레이 가능하면 self.on_world_start_click에서 관리, 불가능하면 클릭했을때 팝업
                self.on_world_start_click if can_play else lambda _: PopupText("플레이 불가", pg.Vector2(SCREEN_SIZE.x / 2, 750), 0, .5),
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
        # 특정 레벨을 선택했다면 메인게임 씬으로 가지않고, 컷씬으로 가게 만든후, 컷씬이 끝나면 컷씬에서 다음씬으로 가게 함
        # 1-1
        if self.selected_chapter == 1 and button.data["index"] == 0:
            self.app.change_scene("tutorial_one_scene")
            return
        # 1-2
        if self.selected_chapter == 1 and button.data["index"] == 1:
            self.app.change_scene("tutorial_two_scene")
            return
        # 2-3
        if self.selected_chapter == 2 and button.data["index"] == 2:
            self.app.change_scene("no_souls_cut_scene")
            return
        # 3-5
        if self.selected_chapter == 3 and button.data["index"] == 4:
            self.app.change_scene("no_lights_cut_scene")
            return
        
        # 컷씬이 없을때엔 그냥 가기
        self.app.registered_scenes["main_game_scene"].current_chapter = self.selected_chapter
        self.app.registered_scenes["main_game_scene"].current_level = button.data["index"]
        self.app.change_scene("main_game_scene")

    def handle_input(self):
        for event in self.app.events:
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.app.change_scene("main_menu_scene")

    def update(self):
        super().update()

        self.handle_input()
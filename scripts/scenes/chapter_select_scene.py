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

# 컷씬 맵 - 챕터, 레벨별로 컷씬 씬 이름 딕셔너리
CUTSCENE_MAP = {
    (1, 0): "tutorial_one_scene",
    (1, 1): "tutorial_two_scene",
    (2, 2): "no_souls_cut_scene",
    (3, 4): "no_lights_cut_scene",
    (4, 0): "boss_intro_cut_scene",
}

class ChapterSelectScene(Scene):
    def on_scene_start(self):
        super().on_scene_start()
        
        self.tilemap = Tilemap(random.choice(TILEMAP_DATA["main_menu_maps"]))
        spawn_all_entities(self.tilemap)
        ImageRenderer(self.app.ASSETS["ui"]["vignette"]["black"], pg.Vector2(0, 0), anchor=pg.Vector2(0, 0))

        TextRenderer("[ESC]", pg.Vector2(10, 10), font_name="bold", font_size=20, anchor=pg.Vector2(0, 0))
        TextRenderer("챕터 선택", pg.Vector2(SCREEN_SIZE.x / 2, 150), font_name="bold", font_size=100, anchor=pg.Vector2(0.5, 0.5))

        ImageButton("select_one", pg.Vector2(450, 270), self.on_chapter_click, None)
        ImageButton("select_two", pg.Vector2(570, 270), self.on_chapter_click, None)
        ImageButton("select_three", pg.Vector2(690, 270), self.on_chapter_click, None)
        ImageButton("select_boss", pg.Vector2(810, 270), self.on_chapter_click, None)

        self.selected_chapter = 0
        self.buttons = []

        self.app.sound_manager.play_bgm("main_menu")

        Sky()
        Clouds()
        Fog()

    def on_chapter_click(self, button: ImageButton):
        name = button.name

        chapter_map = {
            "select_one": 1,
            "select_two": 2,
            "select_three": 3,
            "select_boss": 4
        }
        self.selected_chapter = chapter_map.get(name, 0)

        # 기존 버튼들 제거
        for btn in self.buttons:
            btn.destroy()
        self.buttons.clear()

        chapter_str = str(self.selected_chapter)
        world_names = TILEMAP_DATA["names"][chapter_str]
        progress = self.app.player_data["progress"].get(chapter_str, [])

        last_cleared = -1
        for i, cleared in enumerate(progress):
            if cleared:
                last_cleared = i
        available_idx = last_cleared

        for i, name in enumerate(world_names):
            can_play = i <= available_idx
            score = self.app.player_data["scores"][chapter_str][i]
            btn = TextButton(
                f"< {name} > : [ {score} ]",
                pg.Vector2(200, 400 + i * 60),
                self.on_world_start_click if can_play else lambda _: PopupText("플레이 불가", pg.Vector2(SCREEN_SIZE.x / 2, 750), 0, .5),
                None,
                font_name="bold",
                font_size=32,
                hover_color=pg.Color("blue") if can_play else pg.Color("grey"),
                not_hover_color=pg.Color("white") if can_play else pg.Color("grey"),
                anchor=pg.Vector2(0, .5),
                data={"index": i}
            )
            self.buttons.append(btn)

        self.app.scene.camera.shake_amount += 15

    def on_world_start_click(self, button: TextButton):
        chapter = self.selected_chapter
        level = button.data["index"]
        
        # 컷씬 맵에 있으면 컷씬으로 씬 전환
        if (chapter, level) in CUTSCENE_MAP:
            self.app.change_scene(CUTSCENE_MAP[(chapter, level)])
            return
        
        # 없으면 메인 게임 씬으로 이동하면서 챕터/레벨 세팅
        main_game_scene = self.app.registered_scenes.get("main_game_scene")
        if main_game_scene:
            main_game_scene.current_chapter = chapter
            main_game_scene.current_level = level
        
        self.app.change_scene("main_game_scene")

    def handle_input(self):
        for event in self.app.events:
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.app.change_scene("main_menu_scene")

    def update(self):
        super().update()
        self.handle_input()
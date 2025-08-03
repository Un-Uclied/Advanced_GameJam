import pygame as pg
import pytweening as pt
import json

from scripts.core import *
from scripts.constants import *
from scripts.status import PlayerStatus
from scripts.entities import PlayerCharacter
from scripts.backgrounds import *
from scripts.volume import *
from scripts.tilemap import *
from scripts.ui import *
from .base import Scene

# 타일맵 경로 불러오기
with open("data/tilemap_data.json", 'r') as f:
    data = json.load(f)
    TILEMAP_FILES_BY_CHAPTER = data["maps"]
    LEVEL_NAMES_BY_CHAPTER = data["names"]

class MainGameScene(Scene):
    def __init__(self):
        super().__init__()

        self.player_status = PlayerStatus(self)

        self.current_chapter = 1
        self.current_level = 0

    def on_scene_start(self):
        chapter_str = str(self.current_chapter)
        chapter_maps = TILEMAP_FILES_BY_CHAPTER.get(chapter_str)

        if not chapter_maps:
            print(f"🔥 챕터 {chapter_str} 없음. 메인메뉴로 이동")
            self.app.change_scene("main_menu_scene")
            return

        if self.current_level >= len(chapter_maps):
            # 다음 챕터로 넘어가기
            self.current_chapter += 1
            self.current_level = 0

            next_chapter_str = str(self.current_chapter)
            if next_chapter_str not in TILEMAP_FILES_BY_CHAPTER:
                print("🎉 모든 챕터 클리어! 메인메뉴로")
                self.app.change_scene("main_menu_scene")
                return

            chapter_maps = TILEMAP_FILES_BY_CHAPTER[next_chapter_str]

        # 타일맵 로드
        file_path = chapter_maps[self.current_level]
        self.tilemap = Tilemap(file_path)
        spawn_all_entities(self.tilemap)

        # 플레이어 스폰
        spawn_pos = self.tilemap.get_pos_by_data("spawners_entities", 0)[0]
        self.player_status.player_character = PlayerCharacter(spawn_pos)

        # BGM 재생
        # self.app.sound_manager.play_bgm("boss_bgm")

        self.level_name_text = TextRenderer(
            LEVEL_NAMES_BY_CHAPTER[str(self.current_chapter)][self.current_level],
            SCREEN_SIZE.elementwise() / 2,
            "bold", 50, anchor=pg.Vector2(0.5, 0.5),
        )
        Tween(self.level_name_text, "alpha", 0, 255, duration=1, easing=pt.easeInQuad).on_complete.append(
            lambda: Tween(self.level_name_text, "alpha", 255, 0, duration=2, easing=pt.easeOutQuad)
        )

        super().on_scene_start()
        self.camera.position = pg.Vector2(self.player_status.player_character.rect.center)

        # 배경 효과
        Sky()
        Clouds()
        Fog()

    def update(self):
        self.player_status.update()
        super().update()

    def on_level_end(self):
        self.current_level += 1
        self.app.change_scene("main_game_scene")
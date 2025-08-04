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
with open("data/tilemap_data.json", 'r', encoding="utf-8") as f:
    data = json.load(f)
    TILEMAP_FILES_BY_CHAPTER = data["maps"]
    LEVEL_NAMES_BY_CHAPTER = data["names"]

class MainGameScene(Scene):
    def __init__(self):
        super().__init__()
        self.current_chapter = 1
        self.current_level = 0

    def on_scene_start(self):
        self.vignette = ImageRenderer(self.app.ASSETS["ui"]["vignette"]["black"], pg.Vector2(0, 0), anchor=pg.Vector2(0, 0))

        super().on_scene_start()

        # 다음으로
        self.update_next_progress()

        self.player_status = PlayerStatus(start_health=100)

        # 타일맵 로드
        chapter_str = str(self.current_chapter)
        chapter_maps = TILEMAP_FILES_BY_CHAPTER.get(chapter_str)
        file_path = chapter_maps[self.current_level]
        self.tilemap = Tilemap(file_path)
        spawn_all_entities(self.tilemap)

        # 플레이어 스폰
        spawn_pos = self.tilemap.get_pos_by_data("spawners_entities", 0)[0]
        self.player_status.player_character = PlayerCharacter(spawn_pos)
        self.make_player_ui()

        # BGM 재생
        # self.app.sound_manager.play_bgm("boss_bgm")

        # 레벨 인트로
        self.level_intro()

        # 카메라 위치 플레이어로 
        self.camera.position = pg.Vector2(self.player_status.player_character.rect.center)

        # 배경 효과
        Sky()
        Clouds()
        Fog()

    def update_next_progress(self):
        '''다음 월드로 가기 (현재 챕터끝이면 다음 챕터로 감)'''
        chapter_str = str(self.current_chapter)
        chapter_maps = TILEMAP_FILES_BY_CHAPTER.get(chapter_str)
        # 다음 월드로 넘어가기
        if self.current_level >= len(chapter_maps):
            self.current_chapter += 1
            self.current_level = 0

            next_chapter_str = str(self.current_chapter)
            if next_chapter_str not in TILEMAP_FILES_BY_CHAPTER:
                self.app.change_scene("main_menu_scene")
                return

            chapter_maps = TILEMAP_FILES_BY_CHAPTER[next_chapter_str]

        # 진행상황 저장
        self.app.player_data["progress"][str(self.current_chapter)][self.current_level] = True

    def level_intro(self):
        '''레벨 인트로 (on_scene_start에서 부르기)'''
        self.level_name_text = TextRenderer(
            LEVEL_NAMES_BY_CHAPTER[str(self.current_chapter)][self.current_level],
            SCREEN_SIZE.elementwise() / 2,
            "bold", 50, anchor=pg.Vector2(0.5, 0.5),
        )
        Tween(self.level_name_text, "alpha", 0, 255, duration=1, easing=pt.easeInQuad).on_complete.append(
            lambda: Tween(self.level_name_text, "alpha", 255, 0, duration=2, easing=pt.easeOutQuad)
        )

    def make_player_ui(self):     
        '''플레이어 UI를 여기서 몰아서 생성'''   
        self.player_health_text = TextRenderer(str(self.player_status.health), pg.Vector2(25, 700), font_name="gothic", font_size=64, anchor=pg.Vector2(0, .5))
        
        self.player_invincible_text = TextRenderer("무적 상태", pg.Vector2(25, 680), font_size=30, anchor=pg.Vector2(0, 1))
        self.player_invincible_text.alpha = 0
        self.event_bus.on("on_player_invincible_start", lambda: setattr(self.player_invincible_text, "alpha", 255))
        self.event_bus.on("on_player_invincible_end", lambda: setattr(self.player_invincible_text, "alpha", 0))
        
        self.player_soul_text_one = TextRenderer("영혼 타입 [1]: X", pg.Vector2(25, 580), font_size=30, anchor=pg.Vector2(0, .5))
        self.player_soul_text_two = TextRenderer("영혼 타입 [2]: X", pg.Vector2(25, 620), font_size=30, anchor=pg.Vector2(0, .5))
        self.event_bus.on("on_player_soul_changed", self.on_player_soul_changed)

        self.player_health_warning_text = TextRenderer("체력 낮음!!", pg.Vector2(SCREEN_SIZE.x / 2, 50), font_name="bold", font_size=72, anchor=pg.Vector2(.5, .5))
        self.player_health_warning_text.alpha = 0
        self.event_bus.on("on_player_health_changed", self.on_player_health_changed)

    def on_player_soul_changed(self):
        '''영혼 타입 UI 업뎃'''
        self.player_soul_text_one.text = f"영혼 타입 [1]: {self.player_status.soul_queue[1]}"
        self.player_soul_text_two.text = f"영혼 타입 [2]: {self.player_status.soul_queue[0]}"

    def on_player_health_changed(self):
        '''체력 UI 업뎃'''
        self.player_health_text.text = str(self.player_status.health)
        if self.player_status.health <= 20:
            self.vignette.image = self.app.ASSETS["ui"]["vignette"]["red"]
            self.player_health_warning_text.alpha = 180
        else:
            self.vignette.image = self.app.ASSETS["ui"]["vignette"]["black"]
            self.player_health_warning_text.alpha = 0

    def on_level_end(self):
        '''정상적으로 레벨을 끝까지 가서 portal에 갔을때 호출'''
        self.current_level += 1
        self.app.change_scene("main_game_scene")
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
        # 체력 텍스트랑 체력바
        self.player_health_text = TextRenderer(f"{self.player_status.health} | {self.player_status.max_health}", pg.Vector2(25, 700), font_name="gothic", font_size=64, anchor=pg.Vector2(0, .5))
        self.player_health_bar = ProgressBar(pg.Vector2(25, 740), pg.Vector2(150, 5), self.player_status.health, 0, self.player_status.max_health, anchor=pg.Vector2(0, .5))

        # 무적 상태 표시
        self.player_invincible_text = TextRenderer("무적 상태", pg.Vector2(25, 680), font_size=30, anchor=pg.Vector2(0, 1))
        self.player_invincible_text.alpha = 0
        # 이벤트 리스너 등록
        self.event_bus.connect("on_player_invincible_start", lambda: setattr(self.player_invincible_text, "alpha", 255))
        self.event_bus.connect("on_player_invincible_end",   lambda: setattr(self.player_invincible_text, "alpha", 0))
        
        # 현재 영혼 타입 표시
        self.player_soul_text_one = TextRenderer("영혼 타입 [1]: X", pg.Vector2(25, 580), font_size=30, anchor=pg.Vector2(0, .5))
        self.player_soul_text_two = TextRenderer("영혼 타입 [2]: X", pg.Vector2(25, 620), font_size=30, anchor=pg.Vector2(0, .5))
        # 이벤트 리스너 등록
        self.event_bus.connect("on_player_soul_changed", self.on_player_soul_changed)

        # 체력 낮음 경고
        self.player_health_warning_text = TextRenderer("체력 낮음!!", pg.Vector2(SCREEN_SIZE.x / 2, 50), font_name="bold", font_size=72, anchor=pg.Vector2(.5, .5))
        self.player_health_warning_text.alpha = 0
        # 이벤트 리스너 등록
        self.event_bus.connect("on_player_health_changed", self.on_player_health_changed)

    def on_player_soul_changed(self):
        '''영혼 타입 UI 업뎃'''
        self.player_soul_text_one.text = f"영혼 타입 [1]: {self.player_status.soul_queue[1]}"
        self.player_soul_text_two.text = f"영혼 타입 [2]: {self.player_status.soul_queue[0]}"

    def on_player_health_changed(self):
        '''체력 UI 업뎃'''
        self.player_health_text.text = f"{self.player_status.health} | {self.player_status.max_health}"
        self.player_health_bar.max_val = self.player_status.max_health
        self.player_health_bar.value = self.player_status.health

        # 체력 20이하일때 경고
        if self.player_status.health <= 20:
            self.vignette.image = self.app.ASSETS["ui"]["vignette"]["red"]
            self.player_health_warning_text.alpha = 180
        else:
            self.vignette.image = self.app.ASSETS["ui"]["vignette"]["black"]
            self.player_health_warning_text.alpha = 0

    def on_reset_button_clicked(self, _ : ImageButton):
        self.scene_paused = False
        for i in range(len(self.player_status.soul_queue)):
            self.player_status.soul_queue.append(SOUL_DEFAULT)
        self.on_player_soul_changed()
        self.app.sound_manager.play_sfx(self.app.ASSETS["sounds"]["ui"]["reset"])

    def on_pause_start(self):
        super().on_pause_start()
        self.pause_menu_objects = []
        self.pause_menu_objects.append(ImageRenderer(self.app.ASSETS["ui"]["pause_bg"], pg.Vector2(0, 0), anchor=pg.Vector2(0, 0)))
        for i, soul_type in enumerate(self.player_status.soul_queue):
            self.pause_menu_objects.append(
                ImageRenderer(self.app.ASSETS["ui"]["soul_icons"][soul_type], pg.Vector2(500, 200 + i * 200), scale=4, anchor=pg.Vector2(0, .5))
            )
            self.pause_menu_objects.append(
                TextRenderer(soul_type, pg.Vector2(620, 140 + i * 200), font_name="bold", font_size=35)
            )
            self.pause_menu_objects.append(
                TextRenderer(SOUL_DESCRIPTION[soul_type], pg.Vector2(620, 200 + i * 200), font_name="bold", font_size=20)
            )
        self.pause_menu_objects.append(
            TextRenderer("L\ni\nm\ne\nn", pg.Vector2(15, 5), font_name="gothic", font_size=75)
        )
        self.pause_menu_objects.append(
            TextRenderer("일시 정지", pg.Vector2(80, 20), font_name="bold", font_size=55)
        )
        self.pause_menu_objects.append(
            TextRenderer("챕터 선택으로", pg.Vector2(150, 580), font_size=25, anchor=pg.Vector2(0.5, 0.5))
        )
        self.pause_menu_objects.append(
            # lambda _:가 뭐냐면 버튼의 on_click은 ImageButton을 받을 인수가 있어야하는데, lambda:는 인수를 받지 않아서 에러 터짐. 하지만 ImageButton은 필요하지 않기 때문에 _로 놔둠.
            ImageButton("app_quit", pg.Vector2(150, 650), lambda _: self.app.change_scene("chapter_select_scene"), None)
        )
        self.pause_menu_objects.append(
            ImageButton("restart", pg.Vector2(150, 750), lambda _: self.app.change_scene("main_game_scene"), None)
        )
        self.pause_menu_objects.append(
            ImageButton("reset", pg.Vector2(800, 650), self.on_reset_button_clicked, None)
        )
        PopupText("일시정지 됨.", pg.Vector2(SCREEN_SIZE.x / 2, 730))

    def on_pause_end(self):
        super().on_pause_end()
        for ui in self.pause_menu_objects:
            ui.destroy()
        self.pause_menu_objects.clear()

        PopupText("일시정지 해제.", pg.Vector2(SCREEN_SIZE.x / 2, 760))

    def handle_input(self):
        for event in self.app.events:
            if event.type == pg.KEYDOWN and event.key == pg.K_TAB:
                self.scene_paused = not self.scene_paused

    def update(self):
        self.handle_input()
        super().update()

    def draw(self):
        super().draw()

    def on_level_end(self):
        '''정상적으로 레벨을 끝까지 가서 portal에 갔을때 호출'''
        self.current_level += 1
        self.app.change_scene("main_game_scene")
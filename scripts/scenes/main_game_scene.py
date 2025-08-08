import pygame as pg
import pytweening as pt
import json

from scripts.core import *
from scripts.constants import *
from scripts.status import PlayerStatus
from scripts.enemies import SCORE_UP_MAP
from scripts.entities import PlayerCharacter
from scripts.backgrounds import *
from scripts.volume import *
from scripts.tilemap import *
from scripts.ui import *
from .base import Scene

# 타일맵 경로 데이터 로드
with open("data/tilemap_data.json", 'r', encoding="utf-8") as f:
    data = json.load(f)
    TILEMAP_FILES_BY_CHAPTER = data["maps"]
    LEVEL_NAMES_BY_CHAPTER = data["names"]

class GameUI:
    """
    플레이어 상태를 표시하는 UI를 관리하는 클래스.
    MainGameScene에서 생성되어 플레이어 상태 변화에 반응합니다.
    """
    def __init__(self, scene, player_status, vignette):
        self.scene = scene
        self.player_status = player_status
        self.vignette = vignette
        self._create_all_player_ui()

    def _create_all_player_ui(self):
        """플레이어 상태 표시용 UI를 한 번에 생성하고 이벤트에 연결"""
        self._create_health_ui()
        self._create_invincibility_ui()
        self._create_soul_ui()
        self._create_score_ui()
        self._create_health_warning_ui()

    def _create_health_ui(self):
        """플레이어 체력 관련 UI 생성"""
        self.player_health_text = TextRenderer(f"{self.player_status.health} | {self.player_status.max_health}", pg.Vector2(25, 700), font_name="gothic", font_size=64, anchor=pg.Vector2(0, .5))
        self.player_health_bar = ProgressBar(pg.Vector2(25, 740), pg.Vector2(150, 5), self.player_status.health, 0, self.player_status.max_health, anchor=pg.Vector2(0, .5))
        
        def on_player_health_changed():
            self.player_health_text.text = f"{self.player_status.health} | {self.player_status.max_health}"
            self.player_health_bar.max_val = self.player_status.max_health
            self.player_health_bar.value = self.player_status.health

            if self.player_status.health <= 20:
                self.vignette.image = self.scene.app.ASSETS["ui"]["vignette"]["red"]
                self.player_health_warning_text.alpha = 180
            else:
                self.vignette.image = self.scene.app.ASSETS["ui"]["vignette"]["black"]
                self.player_health_warning_text.alpha = 0

        self.scene.event_bus.connect("on_player_health_changed", lambda: on_player_health_changed())

    def _create_invincibility_ui(self):
        """플레이어 무적 상태 UI 생성"""
        self.player_invincible_text = TextRenderer("무적 상태", pg.Vector2(25, 675), font_size=30, anchor=pg.Vector2(0, 1))
        self.player_invincible_text.alpha = 0

        def on_player_invincible(start):
            self.player_invincible_text.alpha = 255 if start else 0

        self.scene.event_bus.connect("on_player_invincible", on_player_invincible)

    def _create_soul_ui(self):
        """플레이어 영혼 슬롯 UI 생성"""
        self.player_soul_texts = []
        queue = self.player_status.soul_queue
        for i in range(len(queue)):
            slot_index = len(queue) - i
            txt = TextRenderer(f"영혼 타입 [{slot_index}]: {queue[i]}", pg.Vector2(25, 620 - i * 40), font_size=30, anchor=pg.Vector2(0, .5))
            self.player_soul_texts.append(txt)
        
        def on_player_soul_changed():
            queue = self.player_status.soul_queue
        
            # 기존 텍스트가 부족하면 새로 생성
            while len(self.player_soul_texts) < len(queue):
                slot_index = len(self.player_soul_texts) + 1
                y_pos = 620 - (len(self.player_soul_texts)) * 40
                txt = TextRenderer("", pg.Vector2(25, y_pos), font_size=30, anchor=pg.Vector2(0, .5))
                self.player_soul_texts.append(txt)

            # 기존 텍스트 내용 업데이트 및 불필요한 텍스트 파괴
            for i, soul_type in enumerate(queue):
                slot_index = len(queue) - i
                self.player_soul_texts[i].text = f"영혼 타입 [{slot_index}]: {soul_type}"
            
            # 큐가 줄어들었을 경우 남는 텍스트 파괴
            while len(self.player_soul_texts) > len(queue):
                txt_to_destroy = self.player_soul_texts.pop()
                txt_to_destroy.destroy()

        self.scene.event_bus.connect("on_player_soul_changed", lambda: on_player_soul_changed())

    def _create_health_warning_ui(self):
        """체력 경고 텍스트 UI 생성"""
        self.player_health_warning_text = TextRenderer("체력 낮음!!", pg.Vector2(SCREEN_SIZE.x / 2, 50), font_name="bold", font_size=72, anchor=pg.Vector2(.5, .5))
        self.player_health_warning_text.alpha = 0
    
    def _create_score_ui(self):
        self.score_text = TextRenderer(str(self.scene.score), pg.Vector2(25, 25), "gothic", 64)

        def score_changed():
            self.score_text.text = str(self.scene.score)

        self.scene.event_bus.connect("on_score_changed", lambda: score_changed())
        
class PauseUI:
    def __init__(self, scene, player_status):
        self.scene = scene
        self.player_status = player_status
        self.pause_menu_objects = []

    def show(self):
        self.pause_menu_objects.append(ImageRenderer(self.scene.app.ASSETS["ui"]["pause_bg"], pg.Vector2(0, 0), anchor=pg.Vector2(0, 0)))

        # 영혼 슬롯 정보 표시
        for i, soul_type in enumerate(self.player_status.soul_queue):
            y_offset = i * 200
            self.pause_menu_objects.extend([
                ImageRenderer(self.scene.app.ASSETS["ui"]["soul_icons"][soul_type], pg.Vector2(500, 400 - y_offset), scale=4, anchor=pg.Vector2(0, .5)),
                TextRenderer(soul_type, pg.Vector2(620, 340 - y_offset), font_name="bold", font_size=35),
                TextRenderer(SOUL_DESCRIPTION[soul_type], pg.Vector2(620, 400 - y_offset), font_name="bold", font_size=20),
            ])

        # 메뉴 버튼 및 텍스트
        self.pause_menu_objects.extend([
            TextRenderer("L\ni\nm\ne\nn", pg.Vector2(15, 5), font_name="gothic", font_size=75),
            TextRenderer("일시 정지", pg.Vector2(80, 20), font_name="bold", font_size=55),
            TextRenderer("챕터 선택으로", pg.Vector2(150, 580), font_size=25, anchor=pg.Vector2(0.5, 0.5)),
            ImageButton("app_quit", pg.Vector2(150, 650), lambda _: self.scene.app.change_scene("chapter_select_scene"), None),
            ImageButton("restart", pg.Vector2(150, 750), lambda _: self.scene.app.change_scene("main_game_scene"), None),
            ImageButton("reset", pg.Vector2(800, 650), lambda _: self.on_reset_button_clicked(), None),
        ])

        PopupText("일시정지 됨.", pg.Vector2(SCREEN_SIZE.x / 2, 730))

    def hide(self):
        for ui in self.pause_menu_objects:
            ui.destroy()
        self.pause_menu_objects.clear()
        PopupText("일시정지 해제.", pg.Vector2(SCREEN_SIZE.x / 2, 760))

    def on_reset_button_clicked(self):
        """무적 슬롯 초기화 버튼 클릭 시 처리"""
        self.scene_paused = False
        for i in range(len(self.player_status.soul_queue)):
            self.player_status.on_soul_interact(SOUL_DEFAULT)
        self.app.sound_manager.play_sfx(self.app.ASSETS["sounds"]["ui"]["reset"])

class MainGameScene(Scene):
    """
    메인 인게임 씬 클래스. 
    핵심 게임 로직(타일맵, 플레이어)과 UI 클래스를 제어합니다.
    """
    def __init__(self):
        super().__init__()
        self.current_chapter = 1
        self.current_level = 0
        self._score = 0

    def on_scene_start(self):
        """씬이 시작될 때 호출. 배경, 플레이어, UI 등을 초기화한다."""

        # 어두운 비네트 미리 깔아놓기 (FPS 글자 안 가리게)
        self.vignette = ImageRenderer(self.app.ASSETS["ui"]["vignette"]["black"], pg.Vector2(0, 0), anchor=pg.Vector2(0, 0))
        super().on_scene_start()

        # 다음 진행상황 미리 등록
        self.update_next_progress()

        # 플레이어 상태 생성
        self.player_status = PlayerStatus(start_health=100)

        # 타일맵 로드 및 엔티티 생성
        chapter_str = str(self.current_chapter)
        file_path = TILEMAP_FILES_BY_CHAPTER[chapter_str][self.current_level]
        self.tilemap = Tilemap(file_path)
        spawn_all_entities(self.tilemap)
        self.event_bus.connect("on_enemy_died", self.on_enemy_died)

        # 플레이어 생성
        spawn_pos = self.tilemap.get_pos_by_data("spawners_entities", 0)[0]
        self.player_status.player_character = PlayerCharacter(spawn_pos)
        
        # 죽으면 다시 재시작할수 있게
        self.event_bus.connect("on_player_died", lambda: self.app.change_scene("main_game_scene"))

        # UI 클래스 인스턴스 생성 및 초기화
        self.game_ui = GameUI(self, self.player_status, self.vignette)
        self.pause_ui = PauseUI(self, self.player_status)

        # 카메라 초기 위치
        self.camera.position = pg.Vector2(self.player_status.player_character.rect.center)

        # 레벨 이름 텍스트 표시
        self.level_intro()

        # 배경 이펙트
        Sky()
        Clouds()
        Fog()

        # 메인메뉴 또는 이전 판에서 시작된 브금 끄기
        self.app.sound_manager.stop_bgm()

    @property
    def score(self):
        return self._score
    
    @score.setter
    def score(self, value):
        prev = self._score
        self._score += value

        if prev < self._score:
            print("점수가 오름")
        elif prev > self._score:
            print("점수 내려감;")

    def update_next_progress(self):
        """진행 정보 업데이트 (현재 챕터 마지막이면 다음 챕터로)"""
        chapter_str = str(self.current_chapter)
        chapter_maps = TILEMAP_FILES_BY_CHAPTER.get(chapter_str)

        if self.current_level >= len(chapter_maps):
            self.current_chapter += 1
            self.current_level = 0

            if str(self.current_chapter) not in TILEMAP_FILES_BY_CHAPTER:
                self.app.change_scene("main_menu_scene")
                return

        self.app.player_data["progress"][str(self.current_chapter)][self.current_level] = True

    def level_intro(self):
        """레벨 시작 시 화면 중앙에 레벨 이름 보여주기"""
        name = LEVEL_NAMES_BY_CHAPTER[str(self.current_chapter)][self.current_level]
        self.level_name_text = TextRenderer(name, SCREEN_SIZE / 2, "bold", 50, anchor=pg.Vector2(0.5, 0.5))
        Tween(self.level_name_text, "alpha", 0, 255, 1, pt.easeInQuad).on_complete.append(
            lambda: Tween(self.level_name_text, "alpha", 255, 0, 2, pt.easeOutQuad)
        )

    def on_enemy_died(self, enemy_instance):
        """적 사망 시 점수 업데이트"""
        self.score += SCORE_UP_MAP[enemy_instance.__class__]

    def on_pause_start(self):
        """일시정지 진입 시 메뉴 UI 생성"""
        super().on_pause_start()
        self.pause_ui.show()
        
    def on_pause_end(self):
        """일시정지 해제 시 UI 제거"""
        super().on_pause_end()
        self.pause_ui.hide()

    def handle_input(self):
        """입력 처리 (TAB 누르면 일시정지)"""
        for event in self.app.events:
            if event.type == pg.KEYDOWN and event.key == pg.K_TAB:
                self.scene_paused = not self.scene_paused

    def update(self):
        self.handle_input()
        super().update()

    def on_level_end(self):
        """레벨 종료 시 다음 맵으로 이동"""
        self.current_level += 1
        self.app.change_scene("main_game_scene")
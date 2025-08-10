import pygame as pg
import pytweening as pt
import json

from scripts.core import *
from scripts.constants import *
from scripts.status import PlayerStatus
from scripts.enemies import SCORE_UP_MAP, FiveOmega
from scripts.entities import PlayerCharacter
from scripts.backgrounds import *
from scripts.volume import *
from scripts.tilemap import *
from scripts.ui import *
from .base import Scene
from .chapter_select_scene import CUTSCENE_MAP

# 타일맵 데이터 미리 로드 (레벨별 파일, 이름 매핑)
with open("data/tilemap_data.json", 'r', encoding="utf-8") as f:
    data = json.load(f)
    TILEMAP_FILES_BY_CHAPTER = data["maps"]
    LEVEL_NAMES_BY_CHAPTER = data["names"]

class GameUI:
    """
    게임 플레이 UI 전담 클래스
    - 플레이어 상태(체력, 무적, 영혼 등) 표시
    - 점수 표시
    - UI 이벤트 연결 및 갱신 담당
    """
    def __init__(self, scene, player_status, vignette):
        self.scene = scene
        self.player_status = player_status
        self.vignette = vignette
        self._create_all_player_ui()

    def _create_all_player_ui(self):
        self._create_health_ui()
        self._create_invincibility_ui()
        self._create_soul_ui()
        self._create_score_ui()
        self._create_health_warning_ui()

    # 체력 UI 세팅 + 이벤트 연결 (체력 변화 시 텍스트, 바, 비네팅 색 변경)
    def _create_health_ui(self):
        self.player_health_text = TextRenderer(f"{self.player_status.health} | {self.player_status.max_health}", pg.Vector2(25, 700), font_name="gothic", font_size=64, anchor=pg.Vector2(0, .5))
        self.player_health_bar = ProgressBar(pg.Vector2(25, 740), pg.Vector2(150, 5), self.player_status.health, 0, self.player_status.max_health, anchor=pg.Vector2(0, .5))
        
        def on_player_health_changed():
            self.player_health_text.text = f"{self.player_status.health} | {self.player_status.max_health}"
            self.player_health_bar.max_val = self.player_status.max_health
            self.player_health_bar.value = self.player_status.health

            # 체력 20 이하일 때 붉은 비네팅 + 경고 텍스트 알파 증가
            if self.player_status.health <= 20:
                self.vignette.image = self.scene.app.ASSETS["ui"]["vignette"]["red"]
                self.player_health_warning_text.alpha = 180
            else:
                self.vignette.image = self.scene.app.ASSETS["ui"]["vignette"]["black"]
                self.player_health_warning_text.alpha = 0

        self.scene.event_bus.connect("on_player_health_changed", lambda _: on_player_health_changed())

    # 무적 상태 텍스트 표시, 무적 시작/끝에 따라 알파 조절
    def _create_invincibility_ui(self):
        self.player_invincible_text = TextRenderer("무적 상태", pg.Vector2(25, 675), font_size=30, anchor=pg.Vector2(0, 1))
        self.player_invincible_text.alpha = 0

        def on_player_invincible(is_start):
            self.player_invincible_text.alpha = 255 if is_start else 0

        self.scene.event_bus.connect("on_player_invincible", on_player_invincible)

    # 영혼 슬롯 UI: 큐 크기에 따라 텍스트 동적 생성/제거 + 내용 갱신
    def _create_soul_ui(self):
        self.player_soul_texts = []
        queue = self.player_status.soul_queue
        for i in range(len(queue)):
            slot_index = len(queue) - i
            txt = TextRenderer(f"영혼 타입 [{slot_index}]: {queue[i]}", pg.Vector2(25, 620 - i * 40), font_size=30, anchor=pg.Vector2(0, .5))
            self.player_soul_texts.append(txt)
        
        def on_player_soul_changed():
            queue = self.player_status.soul_queue
            # 텍스트 수 부족하면 생성
            while len(self.player_soul_texts) < len(queue):
                slot_index = len(self.player_soul_texts) + 1
                y_pos = 620 - (len(self.player_soul_texts)) * 40
                txt = TextRenderer("", pg.Vector2(25, y_pos), font_size=30, anchor=pg.Vector2(0, .5))
                self.player_soul_texts.append(txt)

            # 내용 갱신
            for i, soul_type in enumerate(queue):
                slot_index = len(queue) - i
                self.player_soul_texts[i].text = f"영혼 타입 [{slot_index}]: {soul_type}"
            
            # 남은 텍스트 파괴
            while len(self.player_soul_texts) > len(queue):
                txt_to_destroy = self.player_soul_texts.pop()
                txt_to_destroy.destroy()

        self.scene.event_bus.connect("on_player_soul_changed", lambda: on_player_soul_changed())

    # 체력 경고 텍스트 (기본 숨김 상태)
    def _create_health_warning_ui(self):
        self.player_health_warning_text = TextRenderer("체력 낮음!!", pg.Vector2(SCREEN_SIZE.x / 2, 50), font_name="bold", font_size=72, anchor=pg.Vector2(.5, .5))
        self.player_health_warning_text.alpha = 0

    # 점수 UI + 점수 변화 시 간단한 스케일 애니메이션 효과
    def _create_score_ui(self):
        self.score_text = TextRenderer(f"[ {self.scene.score} ]", pg.Vector2(100, 50), "gothic", 64, anchor=pg.Vector2(0.5, 0.5))
        def score_changed(score_up):
            self.score_text.text = f"[ {self.scene.score} ]"
            if score_up:
                Tween(self.score_text, "scale", 2, 1, .15, pt.easeInOutQuad, use_unscaled_time=True)
            else:
                Tween(self.score_text, "scale", .5, 1, .15, pt.easeInOutQuad, use_unscaled_time=True)

        self.scene.event_bus.connect("on_score_changed", score_changed)

class PauseUI:
    """일시정지 메뉴 UI 전담 클래스"""
    def __init__(self, scene, player_status):
        self.scene = scene
        self.player_status = player_status
        self.pause_menu_objects = []

    def show(self):
        # 배경, 영혼 슬롯, 텍스트, 버튼 등 UI 요소 생성
        self.pause_menu_objects.append(ImageRenderer(self.scene.app.ASSETS["ui"]["pause_bg"], pg.Vector2(0, 0), anchor=pg.Vector2(0, 0)))

        for i, soul_type in enumerate(self.player_status.soul_queue):
            y_offset = i * 200
            self.pause_menu_objects.extend([
                ImageRenderer(self.scene.app.ASSETS["ui"]["soul_icons"][soul_type], pg.Vector2(500, 400 - y_offset), scale=4, anchor=pg.Vector2(0, .5)),
                TextRenderer(soul_type, pg.Vector2(620, 340 - y_offset), font_name="bold", font_size=35),
                TextRenderer(SOUL_DESCRIPTION[soul_type], pg.Vector2(620, 400 - y_offset), font_name="bold", font_size=20),
            ])

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
        """일시정지 상태에서 무적 슬롯 초기화 버튼 클릭"""
        self.scene.scene_paused = False
        # 큐에 기본 영혼 채우기 (버그방지용)
        for i in range(len(self.player_status.soul_queue)):
            self.player_status.soul_queue.append(SOUL_DEFAULT)
        self.scene.event_bus.emit("on_player_soul_changed")
        self.scene.app.sound_manager.play_sfx(self.scene.app.ASSETS["sounds"]["ui"]["reset"])

class BossUI:
    def __init__(self, scene):
        self.scene = scene
        self.boss : FiveOmega = GameObject.get_objects_by_types(FiveOmega)[0]

        self._create_boss_healthbar()

    def _create_boss_healthbar(self):
        self.health_bar = ProgressBar(pg.Vector2(SCREEN_SIZE.x / 2, 50), pg.Vector2(800, 25), self.boss.status.health, 0, self.boss.status.max_health)
        
        def on_enemy_hit(enemy):
            if not enemy is self.boss:
                return
            self.health_bar.value = self.boss.status.health
        self.scene.event_bus.connect("on_enemy_hit", on_enemy_hit)

class MainGameScene(Scene):
    """
    인게임 씬 전담 클래스
    - 타일맵, 플레이어, UI, 점수, 배경, 사운드, 진행 관리 등
    """
    def __init__(self):
        super().__init__()
        self.current_chapter = 1
        self.current_level = 0

    def on_scene_start(self):
        # 씬 시작 시 비네팅 이미지 미리 깔고
        self.vignette = ImageRenderer(self.app.ASSETS["ui"]["vignette"]["black"], pg.Vector2(0, 0), anchor=pg.Vector2(0, 0))
        super().on_scene_start()

        # 다음 진행상황 미리 업데이트
        self.update_next_progress()

        # 플레이어 상태 초기화 (체력 100)
        self.player_status = PlayerStatus(start_health=100)
        self._score = 0

        # 플레이어 체력 깎이면 점수 -250
        self.event_bus.connect("on_player_hurt", lambda _: setattr(self, "score", self.score - 250))

        # 1초마다 점수 15점씩 감소 타이머
        def on_time_out():
            self.score_down_timer.reset()
            self.score -= 15
        self.score_down_timer = Timer(1, on_time_out, auto_destroy=False)

        # 타일맵 로드 + 엔티티 스폰
        chapter_str = str(self.current_chapter)
        file_path = TILEMAP_FILES_BY_CHAPTER[chapter_str][self.current_level]
        self.tilemap = Tilemap(file_path)
        spawn_all_entities(self.tilemap)

        # 적 죽으면 점수 추가
        self.event_bus.connect("on_enemy_died", lambda instance: setattr(self, "score", self.score + SCORE_UP_MAP[instance.__class__]))

        # 플레이어 캐릭터 생성 + 상태 연결
        spawn_pos = self.tilemap.get_pos_by_data("spawners_entities", 0)[0]
        pc = PlayerCharacter(spawn_pos)
        self.player_status.player_character = pc
        self.player_status.abilities.player_character = pc
        
        # 플레이어 죽으면 씬 재시작
        self.event_bus.connect("on_player_died", lambda: self.app.change_scene("main_game_scene"))

        # UI 인스턴스 생성
        if self.current_chapter == 4 and self.current_level == 0:
            BossUI(self)
        self.game_ui = GameUI(self, self.player_status, self.vignette)
        self.pause_ui = PauseUI(self, self.player_status)

        # 카메라 초기 위치 설정 (플레이어 중심)
        self.camera.position = pg.Vector2(self.player_status.player_character.rect.center)

        # 레벨 이름 텍스트 표시 (페이드 인/아웃)
        self.level_intro()

        # 배경 이펙트 생성
        Sky()
        Clouds()
        Fog()

        # 이전 배경음악 끄기
        self.app.sound_manager.stop_bgm()

    @property
    def score(self):
        return self._score
    
    @score.setter
    def score(self, value):
        prev = self._score
        self._score = max(value, 0)

        # 점수 상승 / 하락 이벤트 발생
        if prev < self._score:
            self.event_bus.emit("on_score_changed", True)
        elif prev > self._score:
            self.event_bus.emit("on_score_changed", False)

    def update_next_progress(self):
        """
        진행 정보 갱신
        - 현재 레벨이 챕터 내 마지막이면 챕터 올리고 레벨 초기화
        - 더 이상 챕터가 없으면 메인 메뉴로
        """
        chapter_str = str(self.current_chapter)
        chapter_maps = TILEMAP_FILES_BY_CHAPTER.get(chapter_str)

        if self.current_level >= len(chapter_maps):
            self.current_chapter += 1
            self.current_level = 0

            if str(self.current_chapter) not in TILEMAP_FILES_BY_CHAPTER:
                self.app.change_scene("main_menu_scene")
                return

        # 플레이어 데이터에 진행상황 저장
        self.app.player_data["progress"][str(self.current_chapter)][self.current_level] = True

    def level_intro(self):
        """레벨 시작 시 중앙에 레벨 이름 텍스트 보여주고 서서히 사라지게 처리"""
        name = LEVEL_NAMES_BY_CHAPTER[str(self.current_chapter)][self.current_level]
        self.level_name_text = TextRenderer(name, SCREEN_SIZE / 2, "bold", 50, anchor=pg.Vector2(0.5, 0.5))
        Tween(self.level_name_text, "alpha", 0, 255, 1, pt.easeInQuad).on_complete.append(
            lambda: Tween(self.level_name_text, "alpha", 255, 0, 2, pt.easeOutQuad)
        )

    def on_enemy_died(self, enemy_instance):
        """적 사망 시 점수 처리 (추가 예정)"""
        pass

    def on_pause_start(self):
        super().on_pause_start()
        self.pause_ui.show()
        
    def on_pause_end(self):
        super().on_pause_end()
        self.pause_ui.hide()

    def handle_input(self):
        """TAB 누르면 일시정지 토글"""
        for event in self.app.events:
            if event.type == pg.KEYDOWN and event.key == pg.K_TAB:
                self.scene_paused = not self.scene_paused

    def update(self):
        self.handle_input()
        super().update()

    def on_level_end(self):
        """
        레벨 종료 처리
        - 무적 상태 부여 (트랜지션 중 사망 방지)
        - 하이스코어 저장
        - 다음 레벨로 넘어감
        - 플레이어 데이터 저장
        """
        self.player_status.current_invincible_time += 99
        if self._score > self.app.player_data["scores"][str(self.current_chapter)][self.current_level]:
            self.app.player_data["scores"][str(self.current_chapter)][self.current_level] = self._score
        
        self._score = 0
        self.current_level += 1

        # 레벨이 ~~라면 컷씬으로 빼돌리기
        target_scene_name = "main_game_scene"
        if (self.current_chapter, self.current_level) in CUTSCENE_MAP:
            target_scene_name = CUTSCENE_MAP[(self.current_chapter, self.current_level)]
            
        self.app.change_scene(target_scene_name)
        self.app.save_player_data()
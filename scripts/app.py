import pygame as pg  # 파이게임 커뮤니티 에디션
import json

from scripts.constants import *  # 앱 이름, 해상도, 화면 설정, 레이어 등이 있음.
from scripts.scenes import *
from scripts.asset_load import *
from scripts.vfx import *
from scripts.ui import *

class SoundManager:
    """
    게임 내 사운드(효과음, 배경음악)를 관리하는 클래스.

    기능:
        - 효과음 채널 풀 관리
        - 사용 가능한 채널에서 SFX 재생
        - BGM 로드 및 재생, 중지
        - SFX 볼륨 개별 조절
    """
    def __init__(self):
        """사운드 매니저 초기화 및 효과음 채널 풀 생성"""
        self.app = App.singleton
        pg.mixer.set_num_channels(MIXER_CHANNEL_COUNT)
        self.sfx_channels = [pg.mixer.Channel(i) for i in range(MIXER_CHANNEL_COUNT)]

    def play_sfx(self, sound: pg.mixer.Sound, volume: float = 1.0):
        """
        사용 가능한 채널에서 효과음을 재생.

        Args:
            sound (pg.mixer.Sound): 재생할 효과음 객체
            volume (float): 효과음 볼륨 (0.0~1.0)
        """
        for ch in self.sfx_channels:
            if not ch.get_busy():
                ch.set_volume(volume * self.app.player_data["vfx_volume"])
                ch.play(sound)
                return

    def play_bgm(self, bgm_name: str, loop: bool = True, fade_ms: int = 1):
        """
        배경음악(BGM)을 로드하여 재생.

        Args:
            bgm_name (str): 재생할 BGM 파일 이름(확장자 제외)
            loop (bool): 무한 반복 여부
            fade_ms (int): 페이드 인 시간 (ms)
        """
        pg.mixer.music.load(f"assets/bgms/{bgm_name}.wav")
        pg.mixer.music.set_volume(self.app.player_data["bgm_volume"])
        pg.mixer.music.play(-1 if loop else 0, fade_ms=fade_ms)

    def stop_bgm(self, fade_ms: int = 1):
        """
        배경음악 재생 중지.

        Args:
            fade_ms (int): 페이드 아웃 시간(ms). 0이면 즉시 중지.
        """
        if fade_ms > 0:
            pg.mixer.music.fadeout(fade_ms)
        else:
            pg.mixer.music.stop()

    def set_sfx_volume(self, volume: float):
        """
        효과음 볼륨 설정.

        Args:
            volume (float): 0.0~1.0 사이 값
        """
        self.sfx_volume = max(0.0, min(1.0, volume))
        for ch in self.sfx_channels:
            ch.set_volume(self.sfx_volume)


class App:
    """
    게임 전체를 관리하는 메인 클래스.
    - Pygame 초기화
    - 씬(Scene) 관리
    - Surface 관리
    - 게임 루프 실행

    Attributes:
        singleton (App): 싱글톤 인스턴스
        screen (Surface): 메인 디스플레이 Surface
        surfaces (dict): 레이어별 Surface
        registered_scenes (dict): 등록된 씬 객체
        scene (Scene): 현재 활성화된 씬
    """
    singleton: 'App' = None

    def __init__(self, start_scene_name: str):
        """
        App 초기화 및 첫 씬 설정.

        Args:
            start_scene_name (str): 처음 시작할 씬 키 (run_game.py에선 "main_menu_scene")
        """
        if App.singleton is not None:
            return App.singleton
        App.singleton = self

        pg.init()
        pg.display.set_caption(APP_NAME)
        self.screen = pg.display.set_mode(SCREEN_SIZE, SCREEN_FLAGS)
        pg.display.set_icon(load_image("app_icon.png"))

        self.surfaces = {
            LAYER_BG: pg.Surface(SCREEN_SIZE, SURFACE_FLAGS).convert_alpha(),
            LAYER_OBJ: pg.Surface(SCREEN_SIZE, SURFACE_FLAGS).convert_alpha(),
            LAYER_ENTITY: pg.Surface(SCREEN_SIZE, SURFACE_FLAGS).convert_alpha(),
            LAYER_VOLUME: pg.Surface(SCREEN_SIZE, SURFACE_FLAGS).convert_alpha(),
            LAYER_DYNAMIC: pg.Surface(SCREEN_SIZE, SURFACE_FLAGS).convert_alpha(),
            LAYER_INTERFACE: pg.Surface(SCREEN_SIZE, SURFACE_FLAGS).convert_alpha(),
        }

        self.load_assets()
        self.load_player_data()

        self.clock = pg.time.Clock()
        self.window_should_be_closed = False
        self.events: list[pg.event.Event] = []
        self.dt: float = 0
        self.unscaled_dt: float = 0
        self.time_scale: float = 1

        self.update_time()
        self.update_event()
        self.sound_manager = SoundManager()

        # 씬 등록
        self.registered_scenes = {
            "main_menu_scene": MainMenuScene(),
            "chapter_select_scene": ChapterSelectScene(),
            "settings_scene": SettingsScene(),
            "info_scene": InfoScene(),
            "main_game_scene": MainGameScene(),
            "editor_scene": TileMapEditScene(),
            "opening_cut_scene": OpeningScene(),
            "tutorial_one_scene": Tutorial1Scene(),
            "tutorial_two_scene": Tutorial2Scene(),
            "no_lights_cut_scene": NoLightCutScene(),
            "no_souls_cut_scene": NoSoulsCutScene(),
        }

        if self.player_data["is_first_start"] and start_scene_name == "main_menu_scene":
            start_scene_name = "opening_cut_scene"

        from scripts.scenes.base import Scene
        self.scene: Scene = self.registered_scenes[start_scene_name]
        self.scene.on_scene_start()
        self.transition = False

        fps_txt = TextRenderer("??", pg.Vector2(SCREEN_SIZE.x, 0), color="green", anchor=pg.Vector2(1, 0))
        fps_txt.update = lambda: setattr(fps_txt, "text", str(int(self.clock.get_fps())))
        ScreenFader(1, False)

    def load_player_data(self):
        """JSON에서 플레이어 데이터 로드."""
        with open("data/player_data.json", "r", encoding="utf-8") as f:
            self.player_data = json.load(f)

    def save_player_data(self):
        """플레이어 데이터 저장."""
        with open('data/player_data.json', 'w', encoding="utf-8") as f:
            json.dump(self.player_data, f, ensure_ascii=False, indent=4)

    def reset_player_data(self):
        """초기 플레이어 데이터로 리셋."""
        with open("data/inital_player_data.json", "r", encoding="utf-8") as f:
            initial_data = json.load(f)
        with open('data/player_data.json', 'w', encoding="utf-8") as f:
            json.dump(initial_data, f, ensure_ascii=False, indent=4)
        self.load_player_data()

    def load_assets(self):
        """모든 게임 에셋 로드."""
        self.ASSETS = load_all_assets()

    def update_time(self):
        """델타타임 및 스케일 적용 시간 업데이트."""
        self.unscaled_dt = self.clock.tick(TARGET_FPS) / 1000
        self.dt = self.unscaled_dt * self.time_scale

    def update_event(self):
        """이벤트 큐 갱신."""
        self.events = pg.event.get()

    def change_scene(self, name: str):
        """
        현재 씬을 다른 씬으로 전환.

        Args:
            name (str): 전환할 씬의 이름
        """
        def on_fade_out_end():
            self.transition = False

        def on_fade_in_end():
            self.scene.on_scene_end()
            self.scene = self.registered_scenes[name]
            self.scene.on_scene_start()

            fps_txt = TextRenderer("??", pg.Vector2(SCREEN_SIZE.x, 0), color="green", anchor=pg.Vector2(1, 0))
            fps_txt.update = lambda: setattr(fps_txt, "text", str(int(self.clock.get_fps())))
            ScreenFader(1, False, on_complete=on_fade_out_end)

        self.transition = True
        ScreenFader(1, True, on_complete=on_fade_in_end)

    def check_for_quit(self):
        """창 닫기 이벤트 감지."""
        for event in self.events:
            if event.type == pg.QUIT:
                self.window_should_be_closed = True

    def clear_surfaces(self):
        """모든 Surface 초기화."""
        self.screen.fill("black")
        for surface in self.surfaces.values():
            surface.fill(pg.Color(0, 0, 0, 0))

    def draw_surfaces(self):
        """모든 Surface를 메인 화면에 그리기."""
        for surface in self.surfaces.values():
            self.screen.blit(surface, (0, 0))

    def run(self):
        """메인 게임 루프."""
        while not self.window_should_be_closed:
            self.update_event()
            self.check_for_quit()
            self.scene.update()

            self.clear_surfaces()
            self.scene.draw()
            self.draw_surfaces()

            pg.display.flip()
            self.update_time()

        self.save_player_data()
        pg.quit()
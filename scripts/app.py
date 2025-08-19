import pygame as pg
import json

from scripts.constants import *
from scripts.scenes import *
from scripts.asset_load import *
from scripts.vfx import *
from scripts.ui import *
from scripts.utils import *

class SoundManager:
    """
    게임 내 사운드(효과음, 배경음악)를 관리하는 클래스.
    
    기능:
        - 효과음 채널 풀 관리
        - 사용 가능한 채널에서 SFX 재생
        - BGM 로드 및 재생, 중지
        - SFX 볼륨 개별 조절
        
    Attributes:
        app (App): 게임 애플리케이션 인스턴스.
        sfx_channels (list): 효과음 재생에 사용되는 Pygame 채널 리스트.
    """
    
    def __init__(self, app):
        """
        사운드 매니저 초기화 및 효과음 채널 풀 생성함.
        
        Args:
            app (App): 게임 애플리케이션 인스턴스.
        """
        # App 인스턴스 저장함. 의존성 주입으로 App 객체를 받아옴.
        self.app = app
        
        # Pygame 믹서에 사용할 총 채널 개수를 설정함.
        pg.mixer.set_num_channels(MIXER_CHANNEL_COUNT)
        
        # 효과음 전용 채널 리스트를 생성함.
        self.sfx_channels = [pg.mixer.Channel(i) for i in range(MIXER_CHANNEL_COUNT)]
        
        # 일시정지된 채널들을 저장할 큐를 초기화함.
        self.paused_channels = []

        self.set_sfx_volume(app.player_data["sfx_volume"])
        self.set_bgm_volume(app.player_data["bgm_volume"])

    def play_sfx(self, sound: pg.mixer.Sound, volume: float = 1.0):
        """
        사용 가능한 채널에서 효과음을 재생함.
        
        게임 설정에 따라 전체 효과음 볼륨을 곱해서 적용함.
        
        Args:
            sound (pg.mixer.Sound): 재생할 효과음 객체.
            volume (float): 효과음 볼륨 (0.0~1.0)
        """
        # 모든 효과음 채널을 순회하면서 사용 가능한 채널을 찾음.
        for channel in self.sfx_channels:
            # 채널이 사용 중이 아닌 경우
            if not channel.get_busy():
                # 앱의 플레이어 데이터에 있는 전체 효과음 볼륨 설정을 적용함.
                final_volume = volume * self.app.player_data.get("sfx_volume", 1.0)
                channel.set_volume(final_volume)
                channel.play(sound)
                return

    def play_bgm(self, bgm_name: str, loop: bool = True, fade_ms: int = 1):
        """
        배경음악(BGM)을 로드하여 재생함.
        
        Args:
            bgm_name (str): 재생할 BGM 파일 이름(확장자 제외).
            loop (bool): 무한 반복 여부.
            fade_ms (int): 페이드 인 시간 (ms).
        """
        # BGM 파일 경로를 생성해서 로드함.
        bgm_path = f"assets/bgms/{bgm_name}.wav"
        pg.mixer.music.load(bgm_path)
        
        # 앱의 플레이어 데이터에 있는 BGM 볼륨 설정을 적용함.
        bgm_volume = self.app.player_data.get("bgm_volume", 1.0)
        pg.mixer.music.set_volume(bgm_volume)
        
        # loop가 True면 무한 반복(-1)하고 아니면 한 번만 재생함(0).
        num_loops = -1 if loop else 0
        pg.mixer.music.play(num_loops, fade_ms=fade_ms)

    def fade_all_sfx(self, milliseconds : int = 500):
        """
        재생되고 있는 모든 효과음들 다 없애기
        """
        
        # 모든 채널을 순회하며 재생 중인 채널을 
        # 다 페이드아웃 -> milliseconds후 자동으로 stop()
        for channel in self.sfx_channels:
            if channel.get_busy():
                channel.fadeout(milliseconds)

    def pause_all_sfx(self):
        """
        재생되고 있는 모든 효과음을 일시정지하고, 일시정지된 채널을 저장함.
        """
        # 일시정지될 채널 리스트를 초기화함.
        self.paused_channels = []
        
        # 모든 채널을 순회하며 재생 중인 채널을 일시정지함.
        for channel in self.sfx_channels:
            if channel.get_busy():
                channel.pause()
                self.paused_channels.append(channel)

    def resume_all_sfx(self):
        """
        일시정지된 모든 효과음을 다시 재생함.
        """
        # 일시정지된 채널 리스트를 순회하며 다시 재생시킴.
        for channel in self.paused_channels:
            channel.unpause()
            
        # 재생 후 일시정지 채널 리스트를 비워줌.
        self.paused_channels = []

    def set_sfx_volume(self, volume: float):
        """
        모든 효과음 채널의 볼륨을 설정함.
        
        Args:
            volume (float): 0.0~1.0 사이 값.
        """
        # 볼륨 값을 0.0에서 1.0 사이로 제한함.
        safe_volume = max(0.0, min(1.0, volume))
        
        # 모든 효과음 채널의 볼륨을 설정함.
        for channel in self.sfx_channels:
            channel.set_volume(safe_volume)

    def set_bgm_volume(self, volume: float):
        """
        배경음악 채널의 볼륨을 설정함.
        
        Args:
            volume (float): 0.0~1.0 사이 값.
        """
        # 볼륨 값을 0.0에서 1.0 사이로 제한함.
        safe_volume = max(0.0, min(1.0, volume))
        
        pg.mixer.music.set_volume(safe_volume)
            
class App:
    """
    게임 전체를 관리하는 메인 클래스.
    - Pygame 초기화
    - 씬(Scene) 관리
    - Surface 관리
    - 게임 루프 실행
    
    Attributes:
        singleton (App): 싱글톤 인스턴스.
        is_debug (bool): 켜져있으면 히트박스를 그림
        screen (Surface): 메인 디스플레이 Surface.
        surfaces (dict): 레이어별 Surface 딕셔너리.
        registered_scenes (dict): 등록된 씬 객체 딕셔너리.
        scene (Scene): 현재 활성화된 씬.
        player_data (dict): 플레이어의 저장 데이터.
        sound_manager (SoundManager): 사운드 관리 인스턴스.
        clock (Clock): 게임 클럭.
        window_should_be_closed (bool): 게임 종료 여부 플래그.
        events (list): Pygame 이벤트 리스트.
        dt (float): 스케일 적용된 델타 타임.
        unscaled_dt (float): 스케일 미적용 델타 타임.
        time_scale (float): 시간 배율.
        
    """
    singleton: 'App' = None
    
    def __new__(cls, *args, **kwargs):
        """
        싱글톤 패턴을 위한 __new__ 메서드 정의.
        """
        # 이미 인스턴스가 존재하면 기존 인스턴스를 반환함.
        if cls.singleton is not None:
            return cls.singleton
            
        # 인스턴스가 없으면 새로 생성해서 반환함.
        instance = super().__new__(cls)
        cls.singleton = instance
        return instance

    def __init__(self, start_scene_name: str):
        """
        App 초기화 및 첫 씬 설정.
        
        Args:
            start_scene_name (str): 처음 시작할 씬 키
        """
        # 이미 초기화된 인스턴스라면 다시 초기화하지 않음.
        if hasattr(self, 'initialized'):
            return
        
        # 초기화 시작 플래그 설정.
        self.initialized = True
        self.is_debug = True

        # Pygame 및 디스플레이 설정 로직을 분리함.
        self.initialize_pygame_and_display()

        # Surface 딕셔너리 설정 로직을 분리함.
        self.create_surfaces()

        # 데이터 및 에셋 로드 로직을 분리함.
        self.load_data_and_assets()

        # 외부에서 많이 접근하는 변수들을 초기화함.
        self.initialize_status()

        # 사운드 매니저를 초기화하고 앱 인스턴스를 전달함.
        self.sound_manager = SoundManager(self)

        # 씬 등록 및 초기 씬 설정 로직을 분리함.
        self.initialize_scenes(start_scene_name)

        # FPS 텍스트 렌더러를 생성함.
        self.create_fps_renderer()
        # 화면 페이드인 효과를 줌.
        ScreenFader(1, False)
        
    def initialize_pygame_and_display(self):
        """Pygame 및 디스플레이 설정을 초기화함."""
        pg.init()
        pg.display.set_caption(APP_NAME)
        self.screen = pg.display.set_mode(SCREEN_SIZE, SCREEN_FLAGS)
        pg.display.set_icon(load_image("app_icon.png"))
        
    def create_surfaces(self):
        """레이어별 Surface를 생성함."""
        self.surfaces = {
            LAYER_BG: pg.Surface(SCREEN_SIZE, SURFACE_FLAGS).convert_alpha(),
            LAYER_OBJ: pg.Surface(SCREEN_SIZE, SURFACE_FLAGS).convert_alpha(),
            LAYER_ENTITY: pg.Surface(SCREEN_SIZE, SURFACE_FLAGS).convert_alpha(),
            LAYER_VOLUME: pg.Surface(SCREEN_SIZE, SURFACE_FLAGS).convert_alpha(),
            LAYER_DYNAMIC: pg.Surface(SCREEN_SIZE, SURFACE_FLAGS).convert_alpha(),
            LAYER_INTERFACE: pg.Surface(SCREEN_SIZE, SURFACE_FLAGS).convert_alpha(),
        }

    def load_data_and_assets(self):
        """플레이어 데이터와 모든 게임 에셋을 로드함."""
        self.load_assets()
        self.load_player_data()

    def load_assets(self):
        """모든 게임 에셋을 로드하고 클래스 변수에 할당함."""
        self.ASSETS = load_all_assets()

    def load_player_data(self):
        """JSON 파일에서 플레이어 데이터를 로드함."""
        try:
            with open("data/player_data.json", "r", encoding="utf-8") as f:
                self.player_data = json.load(f)
        except FileNotFoundError:
            # 파일이 없을 경우 초기 데이터를 로드함.
            self.reset_player_data()

    def save_player_data(self):
        """플레이어 데이터를 JSON 파일에 저장함."""
        with open('data/player_data.json', 'w', encoding="utf-8") as f:
            json.dump(self.player_data, f, ensure_ascii=False, indent=4)

    def reset_player_data(self):
        """초기 플레이어 데이터로 리셋하고 저장함."""
        with open("data/inital_player_data.json", "r", encoding="utf-8") as f:
            initial_data = json.load(f)
        with open('data/player_data.json', 'w', encoding="utf-8") as f:
            json.dump(initial_data, f, ensure_ascii=False, indent=4)
        self.load_player_data()

    def initialize_status(self):
        """외부에서 많이 접근하는 변수들을 초기화함."""
        self.clock = pg.time.Clock()
        self.window_should_be_closed = False
        self.events: list[pg.event.Event] = []
        self.dt: float = 0
        self.unscaled_dt: float = 0
        self.time_scale: float = 1
        self.update_time()
        self.update_event()
        
    def initialize_scenes(self, start_scene_name: str):
        """씬을 등록하고 초기 씬을 설정함."""
        # 씬들을 딕셔너리에 등록함.
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
            "good_ending_cut_scene": GoodEndingCutScene(),
            "bad_ending_cut_scene": BadEndingCutScene(),
            "boss_intro_cut_scene": BossIntroCutScene(),
        }

        # 첫 실행인 경우 시작 씬을 변경함.
        if self.player_data["is_first_start"] and start_scene_name == "main_menu_scene":
            start_scene_name = "opening_cut_scene"

        # 현재 씬을 설정하고 씬 시작 메서드를 호출함.
        from scripts.scenes.base import Scene
        self.scene: Scene = self.registered_scenes[start_scene_name]
        self.scene.on_scene_start()
        self.transition = False

    def create_fps_renderer(self):
        """FPS 표시용 텍스트 렌더러를 생성하고, update 함수를 할당함."""
        fps_text = TextRenderer("??", pg.Vector2(SCREEN_SIZE.x, 0), color="green", anchor=pg.Vector2(1, 0))
        # 람다 함수로 FPS 업데이트 로직을 덮어씀.
        fps_text.update = lambda: setattr(fps_text, "text", str(int(self.clock.get_fps())))

    def update_time(self):
        """델타 타임 및 스케일이 적용된 시간을 업데이트함."""
        self.unscaled_dt = self.clock.tick(TARGET_FPS) / 1000
        self.dt = self.unscaled_dt * self.time_scale

    def update_event(self):
        """이벤트 큐를 갱신함."""
        self.events = pg.event.get()

    def change_scene(self, name: str):
        """
        현재 씬을 다른 씬으로 전환함.
        
        씬 전환 시 페이드 아웃/인 효과를 적용하고, 씬의 시작/종료 메서드를 호출함.
        
        Args:
            name (str): 전환할 씬의 이름.
        """
        # 이미 전환 중인 경우 중복 호출을 막음.
        if self.transition:
            return
        
        # BGM을 서서히 멈춤.
        pg.mixer.music.fadeout(500) # 0.5초
        self.transition = True
        
        # 페이드 인이 완료된 후 실행될 콜백 함수를 정의함.
        def on_fade_in_complete():
            # 이전 씬 종료, 새 씬으로 전환, 새 씬 시작.
            self.scene.on_scene_end()
            self.scene = self.registered_scenes[name]
            self.scene.on_scene_start()
            self.create_fps_renderer()
            
            # 페이드 인 완료 후 페이드 아웃 효과를 줌.
            # 페이드 아웃 완료 후 실행될 콜백 함수를 정의함.
            def on_fade_out_complete():
                self.transition = False
            
            ScreenFader(1, False, on_complete=on_fade_out_complete)

        # 화면 페이드 아웃 효과를 적용하고 콜백을 설정함.
        ScreenFader(1, True, on_complete=on_fade_in_complete)

    def check_for_quit(self):
        """창 닫기 이벤트를 감지하고 종료 플래그를 설정함."""
        for event in self.events:
            if event.type == pg.QUIT:
                self.window_should_be_closed = True

    def clear_surfaces(self):
        """모든 Surface를 검은색으로 초기화함."""
        self.screen.fill("black")
        for surface in self.surfaces.values():
            surface.fill(pg.Color(0, 0, 0, 0))

    def draw_surfaces(self):
        """모든 Surface를 메인 화면에 그림."""
        for surface in self.surfaces.values():
            self.screen.blit(surface, (0, 0))

    def run(self):
        """메인 게임 루프. 게임 실행 중 프레임마다 호출됨."""
        while not self.window_should_be_closed:
            # 이벤트, 업데이트, 렌더링 순서로 게임 루프를 실행함.
            self.update_event()
            self.check_for_quit()
            
            if self.scene:
                self.scene.update()

            self.clear_surfaces()
            if self.scene:
                self.scene.draw()
            self.draw_surfaces()

            pg.display.flip()
            self.update_time()

        # 게임 종료 시 플레이어 데이터를 저장하고 Pygame을 종료함.
        self.save_player_data()
        pg.quit()
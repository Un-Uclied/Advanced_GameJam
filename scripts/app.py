import pygame as pg #파이게임 커뮤니티 에디션

from scripts.constants import * #앱이름, 해상도, 화면 설정, 레이어 등이 있음.
from scripts.scenes import *
from scripts.asset_load import *
from scripts.vfx import *

class SoundManager:
    def __init__(self):
        # BGM 전용 mixer.music 사용
        self.bgm_volume = 1.0

        # 효과음 채널 풀 만들기
        pg.mixer.set_num_channels(MIXER_CHANNEL_COUNT)
        self.sfx_channels = [pg.mixer.Channel(i) for i in range(MIXER_CHANNEL_COUNT)]
        self.sfx_volume = 1.0

    def play_sfx(self, sound: pg.mixer.Sound, volume: float = 1.0):
        """사용 가능한 채널 찾아서 효과음 재생"""
        for ch in self.sfx_channels:
            if not ch.get_busy():
                ch.set_volume(volume * self.sfx_volume)
                ch.play(sound)
                return

    def play_bgm(self, bgm_name : str, loop: bool = True, fade_ms: int = 0):
        """배경음악 재생 (streaming 방식)"""
        pg.mixer.music.load(f"assets/bgms/{bgm_name}.wav")
        pg.mixer.music.set_volume(self.bgm_volume)
        pg.mixer.music.play(-1 if loop else 0, fade_ms=fade_ms)

    def stop_bgm(self, fade_ms: int = 0):
        if fade_ms > 0:
            pg.mixer.music.fadeout(fade_ms)
        else:
            pg.mixer.music.stop()

    def set_bgm_volume(self, volume: float):
        self.bgm_volume = max(0.0, min(1.0, volume))
        pg.mixer.music.set_volume(self.bgm_volume)

    def set_sfx_volume(self, volume: float):
        self.sfx_volume = max(0.0, min(1.0, volume))
        for ch in self.sfx_channels:
            ch.set_volume(self.sfx_volume)

class App:
    '''
    :param start_scene_name: 처음 시작할 씬 키 (run_game.py에선 "main_menu_scene")
    '''
    singleton : 'App' = None
    def __init__(self, start_scene_name : str):
        #싱글톤으로 해서 GameObject __init__에서 접근 가능
        if App.singleton is not None:
            return App.singleton
        App.singleton = self

        #라이브러리 초기화
        pg.init()

        #이름 설정
        pg.display.set_caption(APP_NAME)

        #메인 디스플레이로, 접근은 App에서만
        self.screen = pg.display.set_mode(SCREEN_SIZE, SCREEN_FLAGS)

        #레이어 별로 surface를 만들고, GameObject를 상속받는 클래스마다 원하는곳에 그리거나 접근 가능.
        self.surfaces = {
            LAYER_BG : pg.Surface(SCREEN_SIZE, SURFACE_FLAGS).convert_alpha(),
            LAYER_OBJ : pg.Surface(SCREEN_SIZE, SURFACE_FLAGS).convert_alpha(),
            LAYER_ENTITY : pg.Surface(SCREEN_SIZE, SURFACE_FLAGS).convert_alpha(),
            LAYER_VOLUME : pg.Surface(SCREEN_SIZE, SURFACE_FLAGS).convert_alpha(),
            LAYER_DYNAMIC : pg.Surface(SCREEN_SIZE, SURFACE_FLAGS).convert_alpha(),
            LAYER_INTERFACE : pg.Surface(SCREEN_SIZE, SURFACE_FLAGS).convert_alpha(),
        }

        # 사운드 매니저!!
        self.sound_manager = SoundManager()    

        #모든 애셋 로드, 너무 많으면 프리징 현상 발생
        self.load_assets()

        self.clock = pg.time.Clock()

        self.window_should_be_closed = False

        #현재 이벤트들이 들어가있는 리스트
        # pg.event.get()을 한프레임에 여러번 부르면 성능을 많이 잡아 먹기에, 가장 먼저 이벤트들을 업데이트하고, 게임오브젝트들을 업데이트
        self.events : list[pg.event.Event] = []

        #델타타임
        self.dt : float = 0
        self.unscaled_dt : float = 0
        #타임 스케일 (조절 해서 슬로우 모션 연출 가능)
        self.time_scale : float = 1

        self.update_time()
        self.update_event()

        self.registered_scenes = {
            "main_menu_scene" : MainMenuScene(),
            "settings_scene" : SettingsScene(),
            "info_scene" : InfoScene(),
            "main_game_scene" : MainGameScene(),
            "editor_scene"    : TileMapEditScene()
        }

        self.scene = self.registered_scenes[start_scene_name]
        self.scene.on_scene_start()
        self.transition = False

    def load_assets(self):
        '''모든 에셋 로드'''
        self.ASSETS = load_all_assets()

    def update_time(self):
        '''시간 업데이트'''
        self.unscaled_dt = self.clock.tick(TARGET_FPS) / 1000
        self.dt = self.unscaled_dt * self.time_scale

    def update_event(self):
        '''매프레임 딱 한번만 이벤트 리프레쉬 하도록'''
        self.events = pg.event.get()
    
    def change_scene(self, name : str):
        '''트랜지션과 함께 등록된 씬의 이름을 넣으면 원래씬 종료후 그 씬을 업데이트, 그리기 시작'''
        def on_fade_out_end():
            self.transition = False
        def on_fade_in_end():
            self.scene.on_scene_end()
            self.scene = self.registered_scenes[name]
            self.scene.on_scene_start()
            ScreenFader(1, False, on_complete=on_fade_out_end)
        self.transition = True
        ScreenFader(1, True, on_complete=on_fade_in_end)

    def check_for_quit(self):
        '''종료 이벤트 (이거 없으면 X버튼 눌러도 게임이 안꺼짐)'''
        for event in self.events:
            if event.type == pg.QUIT:
                self.window_should_be_closed = True

    def clear_surfaces(self):
        '''메인 화면 초기화, 다른 surface들은 알파채널까지 없애기'''
        self.screen.fill("black")
        for surface in self.surfaces.values():
            surface.fill(pg.Color(0, 0, 0, 0))

    def draw_surfaces(self):
        '''모든 surface들을 메인 화면에 그리기'''
        for surface in self.surfaces.values():
            self.screen.blit(surface, (0, 0))

    def run(self):
        '''메인 게임 루프'''
        while not self.window_should_be_closed:
            self.update_event()     #1. 제일먼저 이벤트 리슨
            self.check_for_quit()   #2. 종료 확인
            self.scene.update()     #3. 현재 씬 업데이트

            self.clear_surfaces()   #4. 화면 초기화
            
            self.scene.draw()       #5.현재 씬 드로우
            self.draw_surfaces()    #6.surfaces에 그려진것들을 메인 화면에 드로우

            pg.display.flip()       #7.화면 업데이트
            self.update_time()      #8.시간 업데이트
        
        pg.quit()                   #a. 루프 탈출시 정상적으로 종료
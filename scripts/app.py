import pygame as pg

from datas.const import *
from .load_image import *
from .animation import *

from .scenes import *

class App:
    singleton : 'App' = None
    def __init__(self, start_scene_name : str ='test_scene'):
        App.singleton = self

        #파이게임 라이브러리 초기화
        pg.init()
        pg.display.set_caption(GAME_NAME, GAME_NAME)

        #메인 화면 (App.singleton.screen으로 접근 쉽게 가능)
        self.screen = pg.display.set_mode(SCREEN_SIZE, SCREEN_FLAGS, vsync=1)

        #에셋 전부 로드
        self.load_assets()

        self.clock = pg.time.Clock()

        self._window_should_be_closed = False

        #이벤트 리스트, 델타타임 초기화
        self.events : list[pg.event.Event] = []
        self.dt : float = 0

        #이벤트, 델타타임 업데이트 (이벤트는 update마다 가장 먼저 업데이트 됨)
        self._update_time()
        self._update_event()

        #저장된 씬
        self._registered_scenes = {
            "main_game_scene" : MainGameScene(),
            "editor_scene" : TileMapEditScene()
        }
        #__init__() 에 들어온 씬 이름 먼저 시작됨
        self._scene = self._registered_scenes[start_scene_name]
        self._scene.on_scene_start()

    def load_assets(self):
        self.ASSET_TILEMAP = {
            "grass" : load_images("tiles/tiles/grass"),
            "stone"  : load_images("tiles/tiles/stone"),
            "environment" : load_images("tiles/objects/environment"),
            "spawners" : load_images("tiles/spawners")
        }
        self.ASSET_PLAYER = {
           
        }
        self.ANIMATIONS = {
            "player" : {
                "idle" : Animation(load_images("entities/player/idle"), 6, True),
                "run" : Animation(load_images("entities/player/run"), 6, True),
                "jump" : Animation(load_images("entities/player/jump"), 4, False)
            }
        }
        # self.ASSET_ENEMIES = {
        #     "one_alpha" : {}
        # }

    def _update_time(self):
        self.dt = self.clock.tick(TARGET_FPS) / 1000

    def _update_event(self):
        self.events = pg.event.get()
    
    #현재 씬 얻을때 : App.singleton.scene
    @property
    def scene(self) -> Scene:
        return self._scene
    
    #씬 바꿀때는 씬의 이름으로 바꿈 : App.singleton.scene = "씬 이름"
    @scene.setter
    def scene(self, value : str):
        self._scene.on_scene_end()
        self._scene = self._registered_scenes[value]
        self._scene.on_scene_start()

    def _check_for_quit(self):
        for event in self.events:
            if event.type == pg.QUIT:
                self._window_should_be_closed = True

    #메인 게임 루프
    def run(self):
        while not self._window_should_be_closed:
            self._update_event()
            self._check_for_quit()

            self._scene.on_update()

            self.screen.fill("grey")
            self._scene.on_draw()

            pg.display.flip()
            self._update_time()

        pg.quit()

    

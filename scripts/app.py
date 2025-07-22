import pygame as pg

from datas.const import *
from .load_image import *
from .animation import *

from .scenes import *

class App:
    singleton : 'App' = None
    def __init__(self, start_scene_name : str):
        App.singleton = self

        #파이게임 라이브러리 초기화
        pg.init()
        pg.display.set_caption(GAME_NAME, GAME_NAME)

        #메인 화면
        self._screen = pg.display.set_mode(SCREEN_SIZE, SCREEN_FLAGS)
        self.surfaces = {
            LAYER_BG : pg.Surface(SCREEN_SIZE, pg.SRCALPHA),
            LAYER_OBJ : pg.Surface(SCREEN_SIZE, pg.SRCALPHA),
            LAYER_ENTITY : pg.Surface(SCREEN_SIZE, pg.SRCALPHA),
            LAYER_DYNAMIC : pg.Surface(SCREEN_SIZE, pg.SRCALPHA),
            LAYER_VOLUME : pg.Surface(SCREEN_SIZE, pg.SRCALPHA),
            LAYER_INTERFACE : pg.Surface(SCREEN_SIZE, pg.SRCALPHA),
        }

        #에셋 전부 로드
        self.load_assets()

        self.clock = pg.time.Clock()

        self._window_should_be_closed = False

        #이벤트 리스트
        self.events : list[pg.event.Event] = []

        #이벤트, (이벤트는 update마다 가장 먼저 업데이트 됨)
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
            "dirt" : load_images("tiles/tiles/dirt"),
            "folliage" : load_images("tiles/objects/folliage"),
            "props" : load_images("tiles/objects/props"),
            "statues" : load_images("tiles/objects/statues"),
            "spawners" : load_images("tiles/spawners")
        }
        self.ASSET_FONT_PATHS = {
            "default" : "assets/fonts/PF스타더스트 3.0 Bold.ttf"
        }
        self.ASSET_ANIMATIONS = {
            "player" : {
                "idle" : Animation(load_images("entities/player/idle"), 6, True),
                "run" : Animation(load_images("entities/player/run"), 6, True),
                "jump" : Animation(load_images("entities/player/jump"), 4, False)
            }
        }
        self.ASSET_BACKGROUND = {
            "sky" : load_image("skys/night_sky.png", 1)
        }

    def _update_time(self):
        self.clock.tick(TARGET_FPS)

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

    def _clear_screen(self):
        self._screen.fill("brown")
        for layer_name, surface in self.surfaces.items():
            surface.fill(pg.Color(0, 0, 0, 0))

    def _draw_surfaces(self):
        for layer_name, surface in self.surfaces.items():
            self._screen.blit(surface, (0, 0))

    #메인 게임 루프
    def run(self):
        while not self._window_should_be_closed:
            # update
            self._update_event()
            self._check_for_quit()
            self._scene.on_update()

            #screen clear
            self._clear_screen()
            
            #screen draw
            self._scene.on_draw()
            self._draw_surfaces()

            #display update
            pg.display.flip()
            self._update_time()

        pg.quit()
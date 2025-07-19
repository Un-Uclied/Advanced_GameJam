import pygame as pg
import pygame.freetype

from datas.const import *
from .load_image import *

from .scenes import *

class App:
    singleton : 'App' = None
    def __init__(self, start_scene_name : str ='test_scene'):
        App.singleton = self

        pg.init()
        pygame.freetype.init()
        pg.display.set_caption(GAME_NAME, GAME_NAME)

        self.screen = pygame.display.set_mode(SCREEN_SIZE, SCREEN_FLAGS)

        self.load_assets()

        self.clock = pg.time.Clock()

        self._window_should_be_closed = False

        self.events : list[pg.event.Event] = []
        self.dt : float = 0

        self._update_time()
        self._update_event()

        self._registered_scenes = {
            "test_scene" : TestScene(),
            "editor_scene" : TileMapEditScene()
        }
        self._scene = self._registered_scenes[start_scene_name]
        self._scene.on_scene_start()

    def load_assets(self):
        self.ASSET_TILEMAP = {
            "grass" : load_images("tiles/tiles/grass"),
            "stone"  : load_images("tiles/tiles/stone"),
            "environment" : load_images("tiles/objects/environment")
        }

    def _update_time(self):
        self.dt = self.clock.tick(TARGET_FPS) / 1000

    def _update_event(self):
        self.events = pg.event.get()

    @property
    def scene(self) -> Scene:
        return self._scene
    
    @scene.setter
    def scene(self, value : str):
        self._scene.on_scene_end()
        self._scene = self._registered_scenes[value]
        self._scene.on_scene_start()

    def _check_for_quit(self):
        for event in self.events:
            if event.type == pg.QUIT:
                self._window_should_be_closed = True

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

    

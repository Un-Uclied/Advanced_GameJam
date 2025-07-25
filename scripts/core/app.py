import pygame as pg

from datas.const import *
from .load_image import *
from .animation import *

from scripts.scenes.base import Scene
from scripts.scenes import *

mixer_channel_count = 32

class App:
    singleton : 'App' = None
    def __init__(self, start_scene_name : str):
        App.singleton = self

        pg.init()
        pg.display.set_caption(GAME_NAME, GAME_NAME)

        self.screen = pg.display.set_mode(SCREEN_SIZE, SCREEN_FLAGS)
        self.surfaces = {
            LAYER_BG : pg.Surface(SCREEN_SIZE, pg.SRCALPHA),
            LAYER_OBJ : pg.Surface(SCREEN_SIZE, pg.SRCALPHA),
            LAYER_ENTITY : pg.Surface(SCREEN_SIZE, pg.SRCALPHA),
            LAYER_DYNAMIC : pg.Surface(SCREEN_SIZE, pg.SRCALPHA),
            LAYER_VOLUME : pg.Surface(SCREEN_SIZE, pg.SRCALPHA),
            LAYER_INTERFACE : pg.Surface(SCREEN_SIZE, pg.SRCALPHA),
        }

        self.load_assets()

        self.clock = pg.time.Clock()

        self.window_should_be_closed = False

        self.events : list[pg.event.Event] = []
        self.dt : float = 0
        self.time_scale : float = 1

        self.update_time()
        self.update_event()

        self.registered_scenes : dict[str, Scene] = {
            "main_menu_scene" : MainMenuScene(),
            "main_game_scene" : MainGameScene(),
            "editor_scene"    : TileMapEditScene()
        }

        self.scene = self.registered_scenes[start_scene_name]
        self.scene.on_scene_start()

    def load_assets(self):
        self.ASSET_TILEMAP = {
            "dirt"           :  load_images("tiles/tiles/dirt",         tint_color= "grey"),
            "folliage"       :  load_images("tiles/objects/folliage",   tint_color= "grey"),
            "props"          :  load_images("tiles/objects/props",      tint_color= "grey"),
            "statues"        :  load_images("tiles/objects/statues",    tint_color= "grey"),
            "spawners"       :  load_images("tiles/spawners"                              ),
            "enemy_spawners" :  load_images("tiles/enemy_spawners"                        )
        }
        self.ASSET_FONT_PATHS = {
            "default" : "assets/fonts/PF스타더스트 3.0 Bold.ttf"
        }
        self.ASSET_ANIMATIONS = {
            "player" : {
                "idle" : Animation(load_images("entities/player/idle"), .05, True),
                "run"  : Animation(load_images("entities/player/run"),  .08, True),
                "jump" : Animation(load_images("entities/player/jump"),  1,  False)
            },
            "soul" : {
                "idle" : Animation(load_images("entities/soul/idle", 2), .05, True)
            },
            "portal" : {
                "idle" : Animation(load_images("entities/portal/idle", 2), .05, True)
            },
            "one_alpha" : {
                "idle" : Animation(load_images("entities/enemies/1_alpha/idle"), .05, True),
                "run"  : Animation(load_images("entities/enemies/1_alpha/run"), .15, True),
            },
            "one_beta" : {
                "idle" : Animation(load_images("entities/enemies/1_beta/idle"), .05, True),
                "run"  : Animation(load_images("entities/enemies/1_beta/run"), .15, True),
            },
            "two_alpha" : {
                "idle" : Animation(load_images("entities/enemies/2_alpha/idle"), .05, True),
                "run"  : Animation(load_images("entities/enemies/2_alpha/run"), .15, True),
            },
            "two_beta" : {
                "idle" : Animation(load_images("entities/enemies/2_beta/idle"), .05, True),
                "run"  : Animation(load_images("entities/enemies/2_beta/run"), .15, True),
            },
            "three_alpha" : {
                "attack" : Animation(load_images("entities/enemies/3_alpha/attack"), .05, False),
                "run"    : Animation(load_images("entities/enemies/3_alpha/run"), .15, True),
            },
            "three_beta" : {
                "attack" : Animation(load_images("entities/enemies/3_beta/attack"), .05, False),
                "run"    : Animation(load_images("entities/enemies/3_beta/run"), .15, True),
            },
            "four_alpha" : {
                "idle" : Animation(load_images("entities/enemies/4_alpha/idle"), .05, True),
                "run"  : Animation(load_images("entities/enemies/4_alpha/run"), .08, True),
            },
            "four_beta" : {
                "idle" : Animation(load_images("entities/enemies/4_beta/idle"), .05, True),
                "run"  : Animation(load_images("entities/enemies/4_beta/run"), .03, True),
            },
            "five_omega" : {
                "idle" : Animation(load_images("entities/enemies/5_omega/idle"), .05, True),
                "run"  : Animation(load_images("entities/enemies/5_omega/run"), .15, True),
            }
        }
        self.ASSET_BACKGROUND = {
            "sky"     : load_image("skys/night_sky.png", 1),
            "red_sky" : load_image("skys/red_sky.png", .75),
        }
        self.ASSET_UI = {
            "image_button" : {
                "temp" : {
                    "on_hover"     : load_image("ui/buttons/temp/on_hover.png"),
                    "on_not_hover" : load_image("ui/buttons/temp/on_not_hover.png")
                }
            }
        }
        
        pg.mixer.set_num_channels(mixer_channel_count)
        self.ASSET_SFXS = {
            "player" : {
                "jump" : pg.mixer.Sound(BASE_SOUND_PATH + "player/jump.wav"),
                "hurt" : pg.mixer.Sound(BASE_SOUND_PATH + "player/hurt.wav")
            }
        }

    def update_time(self):
        self.dt = self.clock.tick(TARGET_FPS) / 1000 * self.time_scale

    def update_event(self):
        self.events = pg.event.get()
    
    def change_scene(self, name : str):
        self.scene.on_scene_end()
        self.scene = self.registered_scenes[name]
        self.scene.on_scene_start()

    def check_for_quit(self):
        for event in self.events:
            if event.type == pg.QUIT:
                self.window_should_be_closed = True

    def clear_surfaces(self):
        self.screen.fill("brown")
        for surface in self.surfaces.values():
            surface.fill(pg.Color(0, 0, 0, 0))

    def draw_surfaces(self):
        for surface in self.surfaces.values():
            self.screen.blit(surface, (0, 0))

    def run(self):
        while not self.window_should_be_closed:
            self.update_event()
            self.check_for_quit()
            self.scene.on_update()

            self.clear_surfaces()
            
            self.scene.on_draw()
            self.draw_surfaces()

            pg.display.flip()
            self.update_time()
        pg.quit()
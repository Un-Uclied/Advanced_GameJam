import pygame as pg

from scripts.constants import *
from scripts.scenes import *

from .load_image import *
from .animation import *

class App:
    singleton : 'App' = None
    def __init__(self, start_scene_name : str):
        App.singleton = self

        pg.init()
        pg.display.set_caption(APP_NAME)

        self.screen = pg.display.set_mode(SCREEN_SIZE, SCREEN_FLAGS)
        self.surfaces = {
            LAYER_BG : pg.Surface(SCREEN_SIZE, pg.SRCALPHA),
            LAYER_OBJ : pg.Surface(SCREEN_SIZE, pg.SRCALPHA),
            LAYER_ENTITY : pg.Surface(SCREEN_SIZE, pg.SRCALPHA),
            LAYER_DYNAMIC : pg.Surface(SCREEN_SIZE, pg.SRCALPHA),
            LAYER_VOLUME : pg.Surface(SCREEN_SIZE, pg.SRCALPHA),
            LAYER_INTERFACE : pg.Surface(SCREEN_SIZE, pg.SRCALPHA),
        }

        pg.mixer.set_num_channels(MIXER_CHANNEL_COUNT)
        self.load_assets()

        self.clock = pg.time.Clock()

        self.window_should_be_closed = False

        self.events : list[pg.event.Event] = []
        self.dt : float = 0
        self.time_scale : float = 1

        self.update_time()
        self.update_event()

        self.registered_scenes = {
            "main_menu_scene" : MainMenuScene(),
            "main_game_scene" : MainGameScene(),
            "editor_scene"    : TileMapEditScene()
        }

        self.scene = self.registered_scenes[start_scene_name]
        self.scene.on_scene_start()

    def load_assets(self):
        self.ASSETS = {
            "tilemap" : {
                "dirt"           :   load_images("tiles/tiles/dirt", scale=2, tint_color= "grey"),
                "folliage"       :   load_images("tiles/objects/folliage",scale=2, tint_color= "grey"),
                "props"          :   load_images("tiles/objects/props", scale=2, tint_color= "grey"),
                "statues"        :   load_images("tiles/objects/statues", scale=2, tint_color= "grey"),
                "spawners_entities": load_images("tiles/spawners_entities", scale=2,),
                "spawners_enemies" : load_images("tiles/spawners_enemies", scale=2,)
            },

            "fonts" : {
                "default" : "PF스타더스트 3.0 Bold.ttf"
            },

            "animations" : {
                "entities" : {
                    "player" : {
                        "idle" : Animation(load_images("entities/player/idle", scale=2), .05, True),
                        "run"  : Animation(load_images("entities/player/run", scale=2),  .08, True),
                        "jump" : Animation(load_images("entities/player/jump", scale=2),  1,  False)
                    },

                    "soul" : {
                        "idle" : Animation(load_images("entities/soul/idle", scale=2, tint_color="cyan"), .05, True)
                    },

                    "one_alpha" : {
                        "idle" : Animation(load_images("entities/enemies/1_alpha/idle", scale=2), .05, True),
                        "run"  : Animation(load_images("entities/enemies/1_alpha/run", scale=2), .15, True),
                    },
                    "one_beta" : {
                        "idle" : Animation(load_images("entities/enemies/1_beta/idle", scale=2), .05, True),
                        "run"  : Animation(load_images("entities/enemies/1_beta/run", scale=2), .15, True),
                    },
                    "two_alpha" : {
                        "idle" : Animation(load_images("entities/enemies/2_alpha/idle", scale=2), .05, True),
                        "run"  : Animation(load_images("entities/enemies/2_alpha/run", scale=2), .15, True),
                    },
                    "two_beta" : {
                        "idle" : Animation(load_images("entities/enemies/2_beta/idle", scale=2), .05, True),
                        "run"  : Animation(load_images("entities/enemies/2_beta/run", scale=2), .15, True),
                    },
                    "three_alpha" : {
                        "attack" : Animation(load_images("entities/enemies/3_alpha/attack", scale=2), .05, False),
                        "run"    : Animation(load_images("entities/enemies/3_alpha/run", scale=2), .15, True),
                    },
                    "three_beta" : {
                        "attack" : Animation(load_images("entities/enemies/3_beta/attack", scale=2), .05, False),
                        "run"    : Animation(load_images("entities/enemies/3_beta/run", scale=2), .15, True),
                    },
                    "four_alpha" : {
                        "idle" : Animation(load_images("entities/enemies/4_alpha/idle", scale=2), .05, True),
                        "run"  : Animation(load_images("entities/enemies/4_alpha/run", scale=2), .08, True),
                    },
                    "four_beta" : {
                            "idle" : Animation(load_images("entities/enemies/4_beta/idle", scale=2), .05, True),
                        "run"  : Animation(load_images("entities/enemies/4_beta/run", scale=2), .03, True),
                    },
                    "five_omega" : {
                        "idle" : Animation(load_images("entities/enemies/5_omega/idle", scale=2), .05, True),
                        "run"  : Animation(load_images("entities/enemies/5_omega/run", scale=2), .15, True),
                    }
                },
            
                "vfxs" : {
                    "hurt" : Animation(load_images("particles/hurt", scale=2), .03, False),

                    "enemy_attack" : Animation(load_images("particles/enemy_attack", scale=2, tint_color="grey"), .03, False),
                    "enemy_die" : Animation(load_images("particles/enemy_die", scale=2, tint_color="grey"), .03, False),
                    
                    "soul_collect" : Animation(load_images("particles/soul_collect", scale=2), .03, False),
                    
                    "enemy_alpha_projectile_destroy" : Animation(load_images("particles/destroy", scale=2, tint_color="purple"), .03, False),
                    "enemy_beta_projectile_destroy" : Animation(load_images("particles/destroy", scale=2, tint_color="red"), .03, False),

                    "player_projectile_destroy" : Animation(load_images("particles/destroy", scale=2,), .03, False)
                },

                "projectiles" : {
                    "two_alpha" : Animation(load_images("projectiles/projectile", scale=2,tint_color="purple"), .03, True),
                    "two_beta" : Animation(load_images("projectiles/projectile", scale=2, tint_color="red"), .03, True),
                    "player" :  Animation(load_images("projectiles/projectile", scale=2),  .03, True),
                },
            },

            "backgrounds" : {
                "default"     : load_image("skys/night_sky.png", 1),
                "red_sky" : load_image("skys/red_sky.png", .75),
            },

            "ui" : {
                "image_button" : {
                    "temp" : {
                        "on_hover"     : load_image("ui/buttons/temp/on_hover.png"),
                        "on_not_hover" : load_image("ui/buttons/temp/on_not_hover.png")
                    }
                }
            },
            
            "sounds" : {
                "player" : {
                    "jump" :       pg.mixer.Sound("assets/sounds/player/jump.wav"),
                    "hurt" :       pg.mixer.Sound("assets/sounds/player/hurt.wav"),
                    "projectile" : pg.mixer.Sound("assets/sounds/player/projectile.wav"),
                },
                "enemy" : {
                    "attack" :     pg.mixer.Sound("assets/sounds/enemy/attack.wav"),
                    "hurt" :       pg.mixer.Sound("assets/sounds/enemy/hurt.wav"),
                    "die" :        pg.mixer.Sound("assets/sounds/enemy/die.wav"),
                    "projectile" : pg.mixer.Sound("assets/sounds/enemy/projectile.wav"),
                },
                "soul" : {
                    "interact" :   pg.mixer.Sound("assets/sounds/soul/interact.wav"),
                }
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

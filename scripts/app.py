import pygame as pg #파이게임 커뮤니티 에디션

from scripts.constants import * #앱이름, 해상도, 화면 설정, 레이어 등이 있음.
from scripts.scenes import *
from scripts.pre_assets import *#애니메이션 클래스, 이미지 로드 함수

class App:
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
            LAYER_BG : pg.Surface(SCREEN_SIZE, pg.SRCALPHA),
            LAYER_OBJ : pg.Surface(SCREEN_SIZE, pg.SRCALPHA),
            LAYER_ENTITY : pg.Surface(SCREEN_SIZE, pg.SRCALPHA),
            LAYER_VOLUME : pg.Surface(SCREEN_SIZE, pg.SRCALPHA),
            LAYER_DYNAMIC : pg.Surface(SCREEN_SIZE, pg.SRCALPHA),
            LAYER_INTERFACE : pg.Surface(SCREEN_SIZE, pg.SRCALPHA),
        }

        #소리가 너무 많아지면 씹히는 현상 없애려고 채널 개수 늘리기
        pg.mixer.set_num_channels(MIXER_CHANNEL_COUNT)

        #모든 애셋 로드, 너무 많으면 프리징 현상 발생
        self.load_assets()

        self.clock = pg.time.Clock()

        self.window_should_be_closed = False

        #현재 이벤트들이 들어가있는 리스트
        # pg.event.get()을 한프레임에 여러번 부르면 성능을 많이 잡아 먹기에, 가장 먼저 이벤트들을 업데이트하고, 게임오브젝트들을 업데이트
        self.events : list[pg.event.Event] = []

        #델타타임
        self.dt : float = 0
        #타임 스케일 (조절 해서 슬로우 모션 연출 가능)
        self.time_scale : float = 1

        self.update_time()
        self.update_event()

        #순환 참조를 피하기 위해 생성자에서 임포트 ㅜ
        from scripts.scenes.base import Scene
        self.registered_scenes : dict[str, Scene]= {
            "main_menu_scene" : MainMenuScene(),
            "main_game_scene" : MainGameScene(),
            "editor_scene"    : TileMapEditScene()
        }

        self.scene = self.registered_scenes[start_scene_name]
        self.scene.on_scene_start()

    def load_assets(self):
        '''모든 에셋 로드'''
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

                    "portal" : {
                        "idle" : Animation(load_images("entities/portal/idle", scale=2), .05, True)
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
                    "two_alpha_projectile" : Animation(load_images("projectiles/projectile", scale=2,tint_color="purple"), .03, True),
                    "two_beta_projectile" : Animation(load_images("projectiles/projectile", scale=2, tint_color="red"), .03, True),
                    "player_projectile" :  Animation(load_images("projectiles/projectile", scale=2),  .03, True),
                },
            },

            "backgrounds" : {
                "sky" : {
                    "default" : load_images("skys/default", scale=2.5, tint_color=pg.Color(100, 100, 100))
                },
                "clouds" : load_images("clouds", scale=1.5, tint_color="grey")
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
        '''등록된 씬의 이름을 넣으면 원래씬 종료후 그 씬을 업데이트, 그리기 시작'''
        self.scene.on_scene_end()
        self.scene = self.registered_scenes[name]
        self.scene.on_scene_start()

    def check_for_quit(self):
        for event in self.events:
            if event.type == pg.QUIT:
                self.window_should_be_closed = True

    def clear_surfaces(self):
        '''메인 화면 초기화, 다른 surface들은 알파채널까지 없애기'''
        self.screen.fill("red")
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
            self.scene.update()  #3. 현재 씬 업데이트

            self.clear_surfaces()   #4. 화면 초기화
            
            self.scene.draw()    #5.현재 씬 드로우
            self.draw_surfaces()    #6.surfaces에 그려진것들을 메인 화면에 드로우

            pg.display.flip()       #7.화면 업데이트
            self.update_time()      #8.시간 업데이트
        
        pg.quit()                   #a. 루프 탈출시 정상적으로 종료
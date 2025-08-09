import pygame as pg

from scripts.core import *
from scripts.constants import *
from .load_image import *

def load_tilemap_assets():
    return {
        "dirt": load_images("tiles/tiles/dirt", scale=2, tint_color="grey"),
        "stone": load_images("tiles/tiles/stone", scale=2, tint_color="grey"),
        "dead_grass": load_images("tiles/tiles/dead_grass", scale=2, tint_color="grey"),
        "dark_folliage": load_images("tiles/objects/dark_folliage", scale=2, tint_color="grey"),
        "wood_struct": load_images("tiles/tiles/wood_struct", scale=2, tint_color="grey"),
        "dark_rocks": load_images("tiles/objects/dark_rocks", scale=3, tint_color="grey"),
        "grave_woods": load_images("tiles/objects/grave_woods", scale=3, tint_color="grey"),
        "dark_stones": load_images("tiles/objects/dark_stones", scale=2, tint_color="grey"),
        "folliage": load_images("tiles/objects/folliage", scale=2, tint_color="grey"),
        "props": load_images("tiles/objects/props", scale=2, tint_color="grey"),
        "statues": load_images("tiles/objects/statues", scale=2, tint_color="grey"),
        "spawners_entities": load_images("tiles/spawners_entities", scale=2),
        "spawners_enemies": load_images("tiles/spawners_enemies", scale=2),
    }

def load_entity_animations():
    anims = {}

    # 플레이어 애니메이션
    anims["player"] = {
        "idle": Animation(load_images("entities/player/idle", 3), 0.08),
        "run": Animation(load_images("entities/player/run", 3), 0.08),
        "rush": Animation(load_images("entities/player/rush", 3), 0.05),
        "jump": Animation(load_images("entities/player/jump", 3), 0.05),
        "fall": Animation(load_images("entities/player/fall", 3), 0.05),
        "attack" : Animation(load_images("entities/player/attack", 3), 0.04, False),
        "change_soul" : Animation(load_images("entities/player/change_soul", 3), 0.05, False),
        "hurt" : Animation(load_images("entities/player/hurt", 3), 0.25, False),
        "die" : Animation(load_images("entities/player/die", 3), 0.04, False),
    }

    # 소울 애니메이션
    anims["soul"] = {
        "idle": Animation(load_images("entities/soul/idle", 2, "cyan"), 0.05),
    }

    # 포탈 애니메이션
    anims["portal"] = {
        "idle": Animation(load_images("entities/portal/idle", 2), 0.05),
    }

    # 적군 애니메이션 (각 적의 스케일과 속도 등을 직접 명시)
    anims["one_alpha"] = {
        "idle": Animation(load_images("entities/enemies/one_alpha/idle", 2), 0.05),
        "run": Animation(load_images("entities/enemies/one_alpha/run", 2), 0.15),
    }
    anims["one_beta"] = {
        "idle": Animation(load_images("entities/enemies/one_beta/idle", 2), 0.05),
        "run": Animation(load_images("entities/enemies/one_beta/run", 2), 0.15),
    }
    anims["two_alpha"] = {
        "idle": Animation(load_images("entities/enemies/two_alpha/idle", 2), 0.05),
        "run": Animation(load_images("entities/enemies/two_alpha/run", 2), 0.15),
    }
    anims["two_beta"] = {
        "idle": Animation(load_images("entities/enemies/two_beta/idle", 2), 0.05),
        "run": Animation(load_images("entities/enemies/two_beta/run", 2), 0.15),
    }
    anims["three_alpha"] = {
        "attack": Animation(load_images("entities/enemies/three_alpha/attack", 2), 0.05, False),
        "idle": Animation(load_images("entities/enemies/three_alpha/idle", 2), 0.15),
    }
    anims["three_beta"] = {
        "attack": Animation(load_images("entities/enemies/three_beta/attack", 2), 0.05, False),
        "idle": Animation(load_images("entities/enemies/three_beta/idle", 2), 0.15),
    }
    anims["four_alpha"] = {
        "idle": Animation(load_images("entities/enemies/four_alpha/idle", 2), 0.05),
        "run": Animation(load_images("entities/enemies/four_alpha/run", 2), 0.08),
    }
    anims["four_beta"] = {
        "idle": Animation(load_images("entities/enemies/four_beta/idle", 2), 0.05),
        "run": Animation(load_images("entities/enemies/four_beta/run", 2), 0.03),
    }
    # five_omega만 스케일이 1인 점에 유의
    anims["five_omega"] = {
        "idle": Animation(load_images("entities/enemies/five_omega/idle", 1.5), 0.05),
        "run": Animation(load_images("entities/enemies/five_omega/run", 1.5), 0.08),
        "scythe_attack" : Animation(load_images("entities/enemies/five_omega/scythe_attack", 1.5), 0.02, False),
        "turn_eye" : Animation(load_images("entities/enemies/five_omega/turn_eye", 1.5), 0.05, False),
    }

    return anims

def load_vfx_animations():
    return {
        "hurt": Animation(load_images("particles/hurt", scale=2), .03, False),
        "explosion": Animation(load_images("particles/explosion", scale=4), .03, False),
        "enemy" : {
            "attack" : Animation(load_images("particles/enemy/attack", scale=2, tint_color="grey"), .03, False),
            "die": Animation(load_images("particles/enemy/die", scale=2, tint_color="black"), .03, False),
        },
        "soul" : {
            "interact" : Animation(load_images("particles/soul/interact", scale=2), .03, False),
        },
        "portal" : {
            "interact": Animation(load_images("particles/portal/interact", scale=5), .03, False),
        },
        "projectile_destroy" : {
            "enemy_alpha": Animation(load_images("particles/destroy", scale=2, tint_color="purple"), .03, False),
            "enemy_beta": Animation(load_images("particles/destroy", scale=2, tint_color="red"), .03, False),
            "player": Animation(load_images("particles/destroy", scale=2), .03, False),
        },
    }

def load_projectile_animations():
    return {
        "two_alpha_projectile": Animation(load_images("projectiles/projectile", scale=2, tint_color="purple"), .03, True),
        "two_beta_projectile": Animation(load_images("projectiles/projectile", scale=2, tint_color="red"), .03, True),
        "player_projectile": Animation(load_images("projectiles/projectile", scale=2), .03, True),
    }

def load_sound_assets():
    def snd(path):
        return pg.mixer.Sound(f"assets/sounds/{path}.wav")

    return {
        "player": {
            "jump": snd("player/jump"),
            "hurt": snd("player/hurt"),
            "projectile": snd("player/projectile"),
        },
        "enemy": {
            "attack": snd("enemy/attack"),
            "hurt": snd("enemy/hurt"),
            "die": snd("enemy/die"),
            "projectile": snd("enemy/projectile"),
            "boss" : {
                "scythe" : snd("enemy/boss/scythe")
            }
        },
        "soul": {
            "interact": snd("soul/interact"),
        },
        "portal" : {
            "interact" : snd("portal/interact")
        },
        "ui" : {
            "button" : {
                "hover_enter" : snd("ui/button/hover_enter"),
                "hover_exit" : snd("ui/button/hover_exit"),
                "click" : snd("ui/button/click")
            },
            "confirm" : snd("ui/confirm"),
            "next" : snd("ui/next"),
            "reset" : snd("ui/reset")
        }
    }

def load_ui_assets():
    return {
        "image_button": {
            "game_start": {
                "on_hover": load_image("ui/buttons/game_start/on_hover.png", scale=2),
                "on_not_hover": load_image("ui/buttons/game_start/on_not_hover.png", scale=2)
            },
            "app_settings": {
                "on_hover": load_image("ui/buttons/app_settings/on_hover.png", scale=2),
                "on_not_hover": load_image("ui/buttons/app_settings/on_not_hover.png", scale=2)
            },
            "app_info": {
                "on_hover": load_image("ui/buttons/app_info/on_hover.png", scale=2),
                "on_not_hover": load_image("ui/buttons/app_info/on_not_hover.png", scale=2)
            },
            "app_quit": {
                "on_hover": load_image("ui/buttons/app_quit/on_hover.png", scale=2),
                "on_not_hover": load_image("ui/buttons/app_quit/on_not_hover.png", scale=2)
            },
            "select_one": {
                "on_hover": load_image("ui/buttons/chapters/one/on_hover.png"),
                "on_not_hover": load_image("ui/buttons/chapters/one/on_not_hover.png")
            },
            "select_two": {
                "on_hover": load_image("ui/buttons/chapters/two/on_hover.png"),
                "on_not_hover": load_image("ui/buttons/chapters/two/on_not_hover.png")
            },
            "select_three": {
                "on_hover": load_image("ui/buttons/chapters/three/on_hover.png"),
                "on_not_hover": load_image("ui/buttons/chapters/three/on_not_hover.png")
            },
            "select_boss": {
                "on_hover": load_image("ui/buttons/chapters/boss/on_hover.png"),
                "on_not_hover": load_image("ui/buttons/chapters/boss/on_not_hover.png")
            },
            "restart": {
                "on_hover": load_image("ui/buttons/restart/on_hover.png", scale=2),
                "on_not_hover": load_image("ui/buttons/restart/on_not_hover.png", scale=2)
            },
            "reset": {
                "on_hover": load_image("ui/buttons/reset/on_hover.png", scale=2),
                "on_not_hover": load_image("ui/buttons/reset/on_not_hover.png", scale=2)
            },
        },
        "vignette" : {
            "black" : load_image("ui/vignette.png", scale=4, tint_color="black"),
            "red" : load_image("ui/vignette.png", scale=4, tint_color="red"),
        },
        "pause_bg" : load_image("ui/pause_menu.png", scale=4),
        "soul_icons" : {
            SOUL_DEFAULT : load_image("ui/soul_icons/soul_default_icon.png"),
            SOUL_KIND_A : load_image("ui/soul_icons/kind_soul_a_icon.png"),
            SOUL_KIND_B : load_image("ui/soul_icons/kind_soul_b_icon.png"),
            SOUL_KIND_C : load_image("ui/soul_icons/kind_soul_c_icon.png"),
            
            SOUL_EVIL_A : load_image("ui/soul_icons/evil_soul_a_icon.png"),
            SOUL_EVIL_B : load_image("ui/soul_icons/evil_soul_b_icon.png"),
            SOUL_EVIL_C : load_image("ui/soul_icons/evil_soul_c_icon.png")
        }
    }

def load_background_assets():
    return {
        "sky": {
            "default": load_images("skys/default", scale=2.5, tint_color=pg.Color(100, 100, 100)),
            "dark": load_images("skys/dark", scale=2.5, tint_color=pg.Color(100, 100, 100))
        },
        "clouds": load_images("clouds", scale=1.5, tint_color="grey")
    }

def load_cut_scene_assets():
    return {
        "opening" : load_images("cut_scene/opening", scale=2),
        "tutorial_1" : load_images("cut_scene/tutorial_1", scale=2),
        "tutorial_2" : load_images("cut_scene/tutorial_2", scale=2),
    }

def load_all_assets():
    '''엄청 무거우니깐 App클래스에서 딱 한번만 실행하세여'''
    return {
        "tilemap": load_tilemap_assets(),
        "animations": {
            "entities": load_entity_animations(),
            "vfxs": load_vfx_animations(),
            "projectiles": load_projectile_animations(),
        },
        "fonts": {
            "default": "PF스타더스트 3.0 Bold.ttf",
            "gothic" : "Jacquard24-Regular.ttf",
            "bold": "DNFBitBitv2.ttf",
        },
        "sounds": load_sound_assets(),
        "ui": load_ui_assets(),
        "cut_scene": load_cut_scene_assets(),
        "backgrounds": load_background_assets(),
    }
import pygame as pg

from scripts.core import *
from scripts.constants import *
from .load_image import *

def load_tilemap_assets():
    '''타일맵 관련 이미지들 한방에 로드 (타일, 오브젝트 등)'''
    base_args = {"scale": 2, "tint_color": "grey"}
    return {
        "dirt": load_images("tiles/tiles/dirt", **base_args),
        "stone": load_images("tiles/tiles/stone", **base_args),
        "dead_grass": load_images("tiles/tiles/dead_grass", **base_args),
        "dark_folliage": load_images("tiles/objects/dark_folliage", **base_args),
        "wood_struct": load_images("tiles/tiles/wood_struct", **base_args),
        "dark_rocks": load_images("tiles/objects/dark_rocks", scale=3, tint_color="grey"),
        "grave_woods": load_images("tiles/objects/grave_woods", scale=3, tint_color="grey"),
        "dark_stones": load_images("tiles/objects/dark_stones", **base_args),
        "folliage": load_images("tiles/objects/folliage", **base_args),
        "props": load_images("tiles/objects/props", **base_args),
        "statues": load_images("tiles/objects/statues", **base_args),
        "spawners_entities": load_images("tiles/spawners_entities", scale=2),
        "spawners_enemies": load_images("tiles/spawners_enemies", scale=2),
    }

def load_entity_animations():
    '''엔티티 애니메이션 전부 로드 (플레이어, 적, 소울 등)'''
    def anim(path, scale=3, duration=0.08, loop=True):
        return Animation(load_images(path, scale), duration, loop)

    anims = {}

    anims["player"] = {
        "idle": anim("entities/player/idle"),
        "run": anim("entities/player/run"),
        "rush": anim("entities/player/rush", duration=0.05),
        "jump": anim("entities/player/jump", duration=0.05),
        "fall": anim("entities/player/fall", duration=0.05),
        "attack": anim("entities/player/attack", duration=0.04, loop=False),
        "change_soul": anim("entities/player/change_soul", duration=0.05, loop=False),
        "hurt": anim("entities/player/hurt", duration=0.25, loop=False),
        "die": anim("entities/player/die", duration=0.04, loop=False),
    }

    anims["soul"] = {
        "idle": Animation(load_images("entities/soul/idle", 2, "cyan"), 0.05),
    }

    anims["portal"] = {
        "idle": Animation(load_images("entities/portal/idle", 2), 0.05),
    }

    # 적 애니메이션, 기본 스케일 2, idle 0.05초, run 0.15초 기본 세팅
    def enemy_anim(name, scale=2, idle_dur=0.05, run_dur=0.15, extra=None):
        base = {
            "idle": Animation(load_images(f"entities/enemies/{name}/idle", scale), idle_dur),
            "run": Animation(load_images(f"entities/enemies/{name}/run", scale), run_dur),
        }
        if extra:
            base.update(extra)
        return base

    anims["one_alpha"] = enemy_anim("one_alpha")
    anims["one_beta"] = enemy_anim("one_beta")
    anims["two_alpha"] = enemy_anim("two_alpha")
    anims["two_beta"] = enemy_anim("two_beta")

    anims["three_alpha"] = {
        "attack": Animation(load_images("entities/enemies/three_alpha/attack", 2), 0.05, False),
        "idle": Animation(load_images("entities/enemies/three_alpha/idle", 2), 0.15),
    }
    anims["three_beta"] = {
        "attack": Animation(load_images("entities/enemies/three_beta/attack", 2), 0.05, False),
        "idle": Animation(load_images("entities/enemies/three_beta/idle", 2), 0.15),
    }

    anims["four_alpha"] = enemy_anim("four_alpha", run_dur=0.08)
    anims["four_beta"] = enemy_anim("four_beta", run_dur=0.03)

    anims["five_omega"] = {
        "idle": Animation(load_images("entities/enemies/five_omega/idle", 1.5), 0.05),
        "run": Animation(load_images("entities/enemies/five_omega/run", 1.5), 0.08),
        "scythe_attack": Animation(load_images("entities/enemies/five_omega/scythe_attack", 1.5), 0.02, False),
        "turn_eye": Animation(load_images("entities/enemies/five_omega/turn_eye", 1.5), 0.05, False),
    }

    return anims

def load_vfx_animations():
    '''파티클, 이펙트 애니메이션들'''
    return {
        "hurt": Animation(load_images("particles/hurt", scale=2), 0.03, False),
        "explosion": Animation(load_images("particles/explosion", scale=4), 0.03, False),
        "enemy": {
            "attack": Animation(load_images("particles/enemy/attack", scale=2, tint_color="grey"), 0.03, False),
            "die": Animation(load_images("particles/enemy/die", scale=2, tint_color="black"), 0.03, False),
        },
        "soul": {
            "interact": Animation(load_images("particles/soul/interact", scale=2), 0.03, False),
        },
        "portal": {
            "interact": Animation(load_images("particles/portal/interact", scale=5), 0.03, False),
        },
        "projectile_destroy": {
            "enemy_alpha": Animation(load_images("particles/destroy", scale=2, tint_color="purple"), 0.03, False),
            "enemy_beta": Animation(load_images("particles/destroy", scale=2, tint_color="red"), 0.03, False),
            "player": Animation(load_images("particles/destroy", scale=2), 0.03, False),
        },
    }

def load_projectile_animations():
    '''투사체 애니메이션 로드'''
    base_args = {"scale": 2}
    return {
        "two_alpha_projectile": Animation(load_images("projectiles/projectile", tint_color="purple", **base_args), 0.03, True),
        "two_beta_projectile": Animation(load_images("projectiles/projectile", tint_color="red", **base_args), 0.03, True),
        "player_projectile": Animation(load_images("projectiles/projectile", **base_args), 0.03, True),
    }

def load_sound_assets():
    '''사운드 자원 로드, wav만 쓰는 중임'''
    def snd(path):
        return pg.mixer.Sound(f"assets/sounds/{path}.wav")

    return {
        "player": {
            "jump": snd("player/jump"),
            "hurt": snd("player/hurt"),
            "projectile": snd("player/projectile"),
            "dash": snd("player/dash"),  
        },
        "enemy": {
            "attack": snd("enemy/attack"),
            "hurt": snd("enemy/hurt"),
            "die": snd("enemy/die"),
            "projectile": snd("enemy/projectile"),
            "boss": {
                "scythe": snd("enemy/boss/scythe"),
            },
        },
        "soul": {
            "interact": snd("soul/interact"),
        },
        "portal": {
            "interact": snd("portal/interact"),
        },
        "ui": {
            "button": {
                "hover_enter": snd("ui/button/hover_enter"),
                "hover_exit": snd("ui/button/hover_exit"),
                "click": snd("ui/button/click"),
            },
            "confirm": snd("ui/confirm"),
            "next": snd("ui/next"),
            "reset": snd("ui/reset"),
            "unlock": snd("ui/unlock"),
        },
    }

def load_ui_assets():
    '''UI 관련 이미지 로드 (버튼, 아이콘, 배경 등)'''
    def btn_imgs(base_path, scale=2):
        return {
            "on_hover": load_image(f"{base_path}/on_hover.png", scale=scale),
            "on_not_hover": load_image(f"{base_path}/on_not_hover.png", scale=scale),
        }

    return {
        "image_button": {
            "game_start": btn_imgs("ui/buttons/game_start"),
            "app_settings": btn_imgs("ui/buttons/app_settings"),
            "app_info": btn_imgs("ui/buttons/app_info"),
            "app_quit": btn_imgs("ui/buttons/app_quit"),
            "select_one": btn_imgs("ui/buttons/chapters/one", scale=1),
            "select_two": btn_imgs("ui/buttons/chapters/two", scale=1),
            "select_three": btn_imgs("ui/buttons/chapters/three", scale=1),
            "select_boss": btn_imgs("ui/buttons/chapters/boss", scale=1),
            "restart": btn_imgs("ui/buttons/restart"),
            "reset": btn_imgs("ui/buttons/reset"),
        },
        "vignette": {
            "black": load_image("ui/vignette.png", scale=4, tint_color="black"),
            "red": load_image("ui/vignette.png", scale=4, tint_color="red"),
        },
        "pause_bg": load_image("ui/pause_menu.png", scale=4),
        "soul_icons": {
            SOUL_DEFAULT: load_image("ui/soul_icons/soul_default_icon.png"),
            SOUL_KIND_A: load_image("ui/soul_icons/kind_soul_a_icon.png"),
            SOUL_KIND_B: load_image("ui/soul_icons/kind_soul_b_icon.png"),
            SOUL_KIND_C: load_image("ui/soul_icons/kind_soul_c_icon.png"),
            SOUL_EVIL_A: load_image("ui/soul_icons/evil_soul_a_icon.png"),
            SOUL_EVIL_B: load_image("ui/soul_icons/evil_soul_b_icon.png"),
            SOUL_EVIL_C: load_image("ui/soul_icons/evil_soul_c_icon.png"),
        },
    }

def load_background_assets():
    '''배경 이미지 (하늘, 구름 등)'''
    return {
        "sky": {
            "default": load_images("skys/default", scale=2.5, tint_color=pg.Color(100, 100, 100)),
            "dark": load_images("skys/dark", scale=2.5, tint_color=pg.Color(100, 100, 100)),
        },
        "clouds": load_images("clouds", scale=1.5, tint_color="grey"),
    }

def load_cut_scene_assets():
    '''컷씬 이미지들'''
    return {
        "opening": load_images("cut_scene/opening", scale=2),
        "tutorial_1": load_images("cut_scene/tutorial_1", scale=2),
        "tutorial_2": load_images("cut_scene/tutorial_2", scale=2),
        "no_lights": load_images("cut_scene/no_lights", scale=2),
        "no_souls": load_images("cut_scene/no_souls", scale=2),
    }

def load_all_assets():
    '''
    모든 자원을 한방에 로드

    - App 클래스에서 딱 1번만 실행 (엄청 무거움)
    - 리턴값 딕셔너리 구조는 엄청 중요하니 절대 바꾸지 말 것
    '''
    return {
        "tilemap": load_tilemap_assets(),
        "animations": {
            "entities": load_entity_animations(),
            "vfxs": load_vfx_animations(),
            "projectiles": load_projectile_animations(),
        },
        "fonts": {
            "default": "PF스타더스트 3.0 Bold.ttf",
            "gothic": "Jacquard24-Regular.ttf",
            "bold": "DNFBitBitv2.ttf",
        },
        "sounds": load_sound_assets(),
        "ui": load_ui_assets(),
        "cut_scene": load_cut_scene_assets(),
        "backgrounds": load_background_assets(),
    }

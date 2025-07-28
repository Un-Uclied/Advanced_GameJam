import pygame as pg
from .animation import Animation
from .load_image import load_images, load_image

def load_tilemap_assets():
    return {
        "dirt": load_images("tiles/tiles/dirt", scale=2, tint_color="grey"),
        "folliage": load_images("tiles/objects/folliage", scale=2, tint_color="grey"),
        "props": load_images("tiles/objects/props", scale=2, tint_color="grey"),
        "statues": load_images("tiles/objects/statues", scale=2, tint_color="grey"),
        "spawners_entities": load_images("tiles/spawners_entities", scale=2),
        "spawners_enemies": load_images("tiles/spawners_enemies", scale=2),
    }

def load_entity_animations():
    anims = {}
    
    # 기본 애니메이션 셋팅 (이미지는 두배로) (이미지가 작아서 좌표 스케일 자체가 작아지면, 움직임 계산에 문제가 많아서 적당히 크게 하기)
    def anim_set(path, speed, loop, tint=None):
        return Animation(load_images(path, scale=2, tint_color=tint), speed, loop)

    enemies = {
        "one_alpha": {"idle": (.05, True), "run": (.15, True)},
        "one_beta": {"idle": (.05, True), "run": (.15, True)},
        "two_alpha": {"idle": (.05, True), "run": (.15, True)},
        "two_beta": {"idle": (.05, True), "run": (.15, True)},
        "three_alpha": {"attack": (.05, False), "run": (.15, True)},
        "three_beta": {"attack": (.05, False), "run": (.15, True)},
        "four_alpha": {"idle": (.05, True), "run": (.08, True)},
        "four_beta": {"idle": (.05, True), "run": (.03, True)},
        "five_omega": {"idle": (.05, True), "run": (.15, True)},
    }

    for name, actions in enemies.items():
        anims[name] = {}
        for action, (speed, loop) in actions.items():
            anims[name][action] = anim_set(f"entities/enemies/{name}/" + action, speed, loop)

    anims["player"] = {
        "idle": anim_set("entities/player/idle", .05, True),
        "run": anim_set("entities/player/run", .08, True),
        "jump": anim_set("entities/player/jump", 1.0, False),
    }

    anims["soul"] = {
        "idle": anim_set("entities/soul/idle", .05, True, tint="cyan")
    }

    anims["portal"] = {
        "idle": anim_set("entities/portal/idle", .05, True)
    }

    return anims

def load_vfx_animations():
    return {
        "hurt": Animation(load_images("particles/hurt", scale=2), .03, False),
        "enemy_attack": Animation(load_images("particles/enemy_attack", scale=2, tint_color="grey"), .03, False),
        "enemy_die": Animation(load_images("particles/enemy_die", scale=2, tint_color="grey"), .03, False),
        "soul_collect": Animation(load_images("particles/soul_collect", scale=2), .03, False),
        "enemy_alpha_projectile_destroy": Animation(load_images("particles/destroy", scale=2, tint_color="purple"), .03, False),
        "enemy_beta_projectile_destroy": Animation(load_images("particles/destroy", scale=2, tint_color="red"), .03, False),
        "player_projectile_destroy": Animation(load_images("particles/destroy", scale=2), .03, False),
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
        },
        "soul": {
            "interact": snd("soul/interact"),
        }
    }

def load_ui_assets():
    return {
        "image_button": {
            "temp": {
                "on_hover": load_image("ui/buttons/temp/on_hover.png"),
                "on_not_hover": load_image("ui/buttons/temp/on_not_hover.png")
            }
        }
    }

def load_background_assets():
    return {
        "sky": {
            "default": load_images("skys/default", scale=2.5, tint_color=pg.Color(100, 100, 100))
        },
        "clouds": load_images("clouds", scale=1.5, tint_color="grey")
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
            "default": "PF\uc2a4\ud0c0\ub354\uc2a4\ud2b8 3.0 Bold.ttf"
        },
        "sounds": load_sound_assets(),
        "ui": load_ui_assets(),
        "backgrounds": load_background_assets(),
    }
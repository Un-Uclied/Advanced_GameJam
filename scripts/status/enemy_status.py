import pygame as pg
import random

from scripts.constants import *
from scripts.ui import *
from scripts.vfx import AnimatedParticle

ICON_UI_OFFSET = pg.Vector2(40, 0)

class EnemyStatus:
    '''
    적 클래스에서 직접 만들어야하고, GameObject를 상속 받지 않기에 app은 self.enemy.app으로 접근 (좀 돌아가서 접근하는 느낌이 있긴하지만)

    :param enemy: 적 인스턴스!!
    :param max_health: 최대 체력 ㅇㅇ
    '''

    def __init__(self, enemy, max_health : int):
        self.enemy = enemy
        app = self.enemy.app

        self.max_health = max_health
        self._health = self.max_health

        # player_status가 없으면 플레이어가 없는것으로 간주, 타입은 디폴트
        self.soul_type = SOUL_DEFAULT
        if hasattr(app.scene, "player_status"):
            self.soul_type = random.choice(ALL_EVIL_SOUL_TYPES)
            self.make_type_ui()

        # SOUL_EVIL_C가 타입이 되면 여기서 최대 체력 증가
        if self.soul_type == SOUL_EVIL_C:
            self.max_health = max_health + ENEMY_EVIL_C_HEALTH_UP
            self._health = self.max_health
        
        self.hurt_sound = app.ASSETS["sounds"]["enemy"]["hurt"]
        self.hurt_particle_anim = app.ASSETS["animations"]["vfxs"]["hurt"]
        
        self.die_sound = app.ASSETS["sounds"]["enemy"]["die"]
        self.die_particle_anim = app.ASSETS["animations"]["vfxs"]["enemy"]["die"]

    def make_type_ui(self):
        enemy = self.enemy
        app = enemy.app

        self.type_text = TextRenderer(self.soul_type, pg.Vector2(enemy.rect.center) + pg.Vector2(-10, enemy.rect.h / 2) + ICON_UI_OFFSET, anchor=pg.Vector2(1, .5), use_camera=True)
        # TextRenderer의 업데이트를 직접 여기서 바꾸기
        self.type_text.update = self.on_text_update
        
        self.type_icon_image = ImageRenderer(app.ASSETS["ui"]["soul_icons"][self.soul_type], pg.Vector2(enemy.rect.center) + pg.Vector2(10, enemy.rect.h / 2) + ICON_UI_OFFSET, anchor=pg.Vector2(0, .5), use_camera=True)
        # ImageRenderer의 업데이트를 직접 여기서 바꾸기
        self.type_icon_image.update = self.on_icon_update

        self.health_bar = ProgressBar(pg.Vector2(enemy.rect.center) + pg.Vector2(-10, enemy.rect.h / 2 + 15), pg.Vector2(100, 3), self.health, 0, self.max_health, use_camera=True)
        # ProgressBar의 업데이트를 직접 여기서 바꾸기
        self.health_bar.update = self.on_bar_update

    def on_text_update(self):
        self.type_text.pos = pg.Vector2(self.enemy.rect.center) + pg.Vector2(-10, self.enemy.rect.h / 2) + ICON_UI_OFFSET

    def on_icon_update(self):
        self.type_icon_image.pos = pg.Vector2(self.enemy.rect.center) + pg.Vector2(10, self.enemy.rect.h / 2) + ICON_UI_OFFSET

    def on_bar_update(self):
        self.health_bar.pos = pg.Vector2(self.enemy.rect.center) + pg.Vector2(-10, self.enemy.rect.h / 2 + 15)

    def on_enemy_die(self):
        '''내가 만든 UI다 지우기'''
        self.type_text.destroy()
        self.type_icon_image.destroy()
        self.health_bar.destroy()

    @property
    def health(self):
        return self._health
    
    @health.setter
    def health(self, value):

        before_health = self._health
        self._health = max(min(value, self.max_health), 0)

        app = self.enemy.app
        camera = app.scene.camera

        if before_health > self._health:
            #체력이 깎인 만큼 카메라 흔들기
            camera.shake_amount += before_health - self._health
            # 체력바에도 적용
            self.health_bar.value = self._health

            #죽을때와 체력이 깎일때 효과음 | 파티클이 다르게끔
            if self._health > 0:
                app.sound_manager.play_sfx(self.hurt_sound)
                AnimatedParticle(self.hurt_particle_anim, pg.Vector2(self.enemy.rect.center))
            else:
                app.sound_manager.play_sfx(self.die_sound)
                AnimatedParticle(self.die_particle_anim, pg.Vector2(self.enemy.rect.center))
        
        #0이 되면 제거
        if self._health <= 0:
            self.enemy.destroy()
            self.on_enemy_die()
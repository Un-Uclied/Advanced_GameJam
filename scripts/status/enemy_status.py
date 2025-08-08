import pygame as pg
import random

from scripts.constants import *
from scripts.ui import *
from scripts.vfx import AnimatedParticle
from scripts.core import GameObject

ICON_UI_OFFSET = pg.Vector2(40, 0)

class EnemyUI(GameObject):
    """적의 UI 요소를 관리하는 클래스 (체력바, 아이콘 등)"""
    def __init__(self, enemy, soul_type, max_health):
        super().__init__()
        self.enemy = enemy
        self.soul_type = soul_type
        self.max_health = max_health
        self._create_ui_elements()

    def _create_ui_elements(self):
        """UI 요소 생성 및 초기 설정"""
        app = self.app

        self.type_text = TextRenderer(self.soul_type, pg.Vector2(0, 0), anchor=pg.Vector2(1, .5), use_camera=True)
        self.type_icon_image = ImageRenderer(app.ASSETS["ui"]["soul_icons"][self.soul_type], pg.Vector2(0, 0), anchor=pg.Vector2(0, .5), use_camera=True)
        self.health_bar = ProgressBar(pg.Vector2(0, 0), pg.Vector2(100, 3), self.max_health, 0, self.max_health, use_camera=True)

    def update(self):
        """매 프레임마다 UI 위치 업데이트"""
        pos_offset = pg.Vector2(0, self.enemy.rect.h / 2)
        text_pos = pg.Vector2(self.enemy.rect.center) + pg.Vector2(-10, 0) + pos_offset + ICON_UI_OFFSET
        icon_pos = pg.Vector2(self.enemy.rect.center) + pg.Vector2(10, 0) + pos_offset + ICON_UI_OFFSET
        bar_pos = pg.Vector2(self.enemy.rect.center) + pg.Vector2(-10, 15) + pos_offset

        self.type_text.pos = text_pos
        self.type_icon_image.pos = icon_pos
        self.health_bar.pos = bar_pos
        super().update()

    def update_health_bar(self, current_health):
        """체력바 값 업데이트"""
        self.health_bar.value = current_health

    def destroy(self):
        """모든 UI 요소 제거"""
        self.type_text.destroy()
        self.type_icon_image.destroy()
        self.health_bar.destroy()
        super().destroy()

class EnemyStatus:
    """적의 상태(체력, 타입)를 관리하는 클래스"""
    def __init__(self, enemy, max_health: int):
        self.enemy = enemy
        app = self.enemy.app

        self.max_health = max_health
        self._health = self.max_health

        self.soul_type = SOUL_DEFAULT
        if hasattr(app.scene, "player_status"):
            self.soul_type = random.choice(ALL_EVIL_SOUL_TYPES)

        if self.soul_type == SOUL_EVIL_C:
            self.max_health = max_health + ENEMY_EVIL_C_HEALTH_UP
            self._health = self.max_health
        
        self.hurt_sound = app.ASSETS["sounds"]["enemy"]["hurt"]
        self.hurt_particle_anim = app.ASSETS["animations"]["vfxs"]["hurt"]
        self.die_sound = app.ASSETS["sounds"]["enemy"]["die"]
        self.die_particle_anim = app.ASSETS["animations"]["vfxs"]["enemy"]["die"]

        # EnemyUI 인스턴스 생성
        if hasattr(app.scene, "player_status"):
            self.enemy_ui = EnemyUI(self.enemy, self.soul_type, self.max_health)

    def on_enemy_die(self):
        """적 사망 시 호출되는 로직"""
        if hasattr(self, "enemy_ui"):
            self.enemy_ui.destroy()
        self.enemy.app.scene.event_bus.emit("on_enemy_died", self.enemy)

    def on_enemy_hit(self):
        self.enemy.app.scene.event_bus.emit("on_enemy_hit", self.enemy)

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
            camera.shake_amount += before_health - self._health
            if hasattr(self, "enemy_ui"):
                self.enemy_ui.update_health_bar(self._health)

            if self._health > 0:
                app.sound_manager.play_sfx(self.hurt_sound)
                AnimatedParticle(self.hurt_particle_anim, pg.Vector2(self.enemy.rect.center))
                self.on_enemy_hit()
            else:
                app.sound_manager.play_sfx(self.die_sound)
                AnimatedParticle(self.die_particle_anim, pg.Vector2(self.enemy.rect.center))
                self.enemy.destroy()
                self.on_enemy_die()
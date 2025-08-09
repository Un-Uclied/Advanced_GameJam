import pygame as pg
import random

from scripts.constants import *
from scripts.ui import *
from scripts.vfx import AnimatedParticle
from scripts.core import GameObject

ICON_UI_OFFSET = pg.Vector2(40, 0)

class EnemyUI(GameObject):
    """
    적 전용 UI 관리 클래스 (체력바, 영혼 타입 텍스트, 아이콘)
    
    :param enemy: UI가 붙을 적 객체
    :param soul_type: 적의 영혼 타입 (문자열)
    :param max_health: 적 최대 체력
    """
    def __init__(self, enemy, soul_type, max_health):
        super().__init__()
        self.enemy = enemy
        self.soul_type = soul_type
        self.max_health = max_health
        self._create_ui_elements()

    def _create_ui_elements(self):
        """UI 텍스트, 아이콘, 체력바 생성 및 초기 위치 세팅"""
        app = self.app
        self.type_text = TextRenderer(
            self.soul_type, pg.Vector2(0, 0), anchor=pg.Vector2(1, 0.5), use_camera=True
        )
        self.type_icon_image = ImageRenderer(
            app.ASSETS["ui"]["soul_icons"][self.soul_type],
            pg.Vector2(0, 0),
            anchor=pg.Vector2(0, 0.5),
            use_camera=True
        )
        self.health_bar = ProgressBar(
            pg.Vector2(0, 0),
            pg.Vector2(100, 3),
            self.max_health,
            0,
            self.max_health,
            use_camera=True
        )

    def update(self):
        """매 프레임 적 위치에 맞춰 UI 위치 업데이트"""
        pos_offset = pg.Vector2(0, self.enemy.rect.height / 2)
        base_center = pg.Vector2(self.enemy.rect.center)
        
        self.type_text.pos = base_center + pg.Vector2(-10, 0) + pos_offset + ICON_UI_OFFSET
        self.type_icon_image.pos = base_center + pg.Vector2(10, 0) + pos_offset + ICON_UI_OFFSET
        self.health_bar.pos = base_center + pg.Vector2(-10, 15) + pos_offset
        
        super().update()

    def update_health_bar(self, current_health):
        """체력바 값 변경"""
        self.health_bar.value = current_health

    def destroy(self):
        """UI 관련 객체 모두 안전하게 제거"""
        self.type_text.destroy()
        self.type_icon_image.destroy()
        self.health_bar.destroy()
        super().destroy()

class EnemyStatus:
    """
    적 상태 관리 클래스 (체력, 영혼 타입, 사망, 피격 이펙트 처리)
    
    :param enemy: 소유 적 객체
    :param max_health: 적 최대 체력 초기값
    """
    def __init__(self, enemy, max_health: int):
        self.enemy = enemy
        self.app = enemy.app

        # 영혼 타입 및 체력 설정
        self.soul_type = SOUL_DEFAULT
        if hasattr(self.app.scene, "player_status"):
            self.soul_type = random.choice(ALL_EVIL_SOUL_TYPES)

        self.max_health = max_health
        if self.soul_type == SOUL_EVIL_C:
            self.max_health += ENEMY_EVIL_C_HEALTH_UP

        self._health = self.max_health

        # 사운드 & 파티클 준비
        self.hurt_sound = self.app.ASSETS["sounds"]["enemy"]["hurt"]
        self.hurt_particle_anim = self.app.ASSETS["animations"]["vfxs"]["hurt"]
        self.die_sound = self.app.ASSETS["sounds"]["enemy"]["die"]
        self.die_particle_anim = self.app.ASSETS["animations"]["vfxs"]["enemy"]["die"]

        # UI 생성 (플레이어 상태 존재할 때만)
        self.enemy_ui = None
        if hasattr(self.app.scene, "player_status"):
            self.enemy_ui = EnemyUI(self.enemy, self.soul_type, self.max_health)

    def on_enemy_die(self):
        """적 사망 시 처리 - UI 제거 및 이벤트 발생"""
        if self.enemy_ui:
            self.enemy_ui.destroy()
        self.app.scene.event_bus.emit("on_enemy_died", self.enemy)

    def on_enemy_hit(self):
        """적 피격 시 이벤트 발생"""
        self.app.scene.event_bus.emit("on_enemy_hit", self.enemy)

    @property
    def health(self):
        return self._health
    
    @health.setter
    def health(self, value):
        before_health = self._health
        self._health = max(0, min(value, self.max_health))

        if before_health > self._health:
            # 카메라 흔들림 강도는 입은 대미지 차이
            self.app.scene.camera.shake_amount += before_health - self._health
            
            if self.enemy_ui:
                self.enemy_ui.update_health_bar(self._health)

            # 피격 효과 재생 및 이벤트 호출
            if self._health > 0:
                self.app.sound_manager.play_sfx(self.hurt_sound)
                AnimatedParticle(self.hurt_particle_anim, pg.Vector2(self.enemy.rect.center))
                self.on_enemy_hit()
            else:
                # 사망 효과 재생 및 적 제거
                self.app.sound_manager.play_sfx(self.die_sound)
                AnimatedParticle(self.die_particle_anim, pg.Vector2(self.enemy.rect.center))
                self.enemy.destroy()
                self.on_enemy_die()
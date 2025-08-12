import pygame as pg

from scripts.ui import TextRenderer
from scripts.vfx import *
from scripts.core import Tween
from .base import Entity

HIT_BOX_SIZE = (180, 190)
LIGHT_SIZE = 500

class Portal(Entity):
    """
    플레이어가 들어가면 레벨 클리어 처리하는 포탈 엔티티
    
    - 플레이어가 포탈 안에 있으면 'F키로 균열 진입' 힌트 UI 표시
    - F키 입력 시 인터랙트 처리 (한 번만)
    - 포탈 빛 및 효과 애니메이션 관리
    """

    def __init__(self, spawn_position: pg.Vector2):
        rect = pg.Rect(spawn_position, HIT_BOX_SIZE)
        super().__init__("portal", rect)

        # 빛 효과 생성
        from scripts.volume import Light
        self.light = Light(LIGHT_SIZE, pg.Vector2(self.rect.center))

        self.interacted = False
        self.interact_sound = self.app.ASSETS["sounds"]["portal"]["interact"]
        self.interact_particle_anim = self.app.ASSETS["animations"]["vfxs"]["portal"]["interact"]

        # 힌트 텍스트 UI (월드 스페이스)
        self.hint_ui = TextRenderer(
            "[F] 키로 균열 진입",
            pg.Vector2(self.rect.centerx, self.rect.top - 30),
            anchor=pg.Vector2(0.5, 1.0),
            use_camera=True
        )
        self.hint_ui.alpha = 0  # 기본은 투명

        self.player_was_inside = False  # 플레이어가 이전 프레임에 포탈 안에 있었는지 여부
        self.current_tween = None       # 힌트 UI alpha 조절용 Tween

    @property
    def is_player_inside(self) -> bool:
        """플레이어가 포탈 영역 안에 있는지 체크"""
        ps = self.app.scene.player_status
        pc = ps.player_character
        return self.rect.colliderect(pc.rect)

    def handle_hint_ui(self):
        """포탈 내외부 입장에 따라 힌트 UI의 투명도 Tween 조절"""
        if self.is_player_inside and not self.player_was_inside:
            # 플레이어가 새로 포탈 안으로 들어왔을 때
            if self.current_tween:
                self.current_tween.destroy()
            self.current_tween = Tween(self.hint_ui, "alpha", self.hint_ui.alpha, 255, 0.3)
            self.player_was_inside = True

        elif not self.is_player_inside and self.player_was_inside:
            # 플레이어가 포탈 밖으로 나갔을 때
            if self.current_tween:
                self.current_tween.destroy()
            self.current_tween = Tween(self.hint_ui, "alpha", self.hint_ui.alpha, 0, 0.3)
            self.player_was_inside = False

    def interact(self):
        """플레이어가 F키로 포탈 진입 시 처리"""
        if self.interacted:
            return

        self.interacted = True

        self.app.scene.on_level_end()
        self.app.sound_manager.play_sfx(self.interact_sound)
        AnimatedParticle(self.interact_particle_anim, pg.Vector2(self.rect.center))
        self.app.scene.camera.shake_amount += 25

    def handle_input(self):
        """포탈 상호작용 입력 처리 (F키)"""
        for event in self.app.events:
            if event.type == pg.KEYDOWN and event.key == pg.K_f:
                if self.is_player_inside and not self.interacted:
                    self.interact()

    def update(self):
        super().update()
        self.handle_hint_ui()
        self.handle_input()
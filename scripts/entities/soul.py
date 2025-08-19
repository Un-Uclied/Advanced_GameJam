import pygame as pg
import random

from scripts.ai import *
from scripts.vfx import *
from scripts.constants import *
from scripts.volume import *
from scripts.ui import *
from scripts.utils import *
from .base import PhysicsEntity

HIT_BOX_SIZE = (40, 50)

MOVE_SPEED = 1
MIN_CHANGE_TIMER = 0.8
MAX_CHANGE_TIMER = 1.5

LIGHT_SIZE = 300
LIGHT_STRENGTH = 30

FLIP_OFFSET = {
    False: pg.Vector2(5, -20),
    True: pg.Vector2(5, -20)
}

class Soul(PhysicsEntity):
    """
    움직이는 소울 오브젝트

    - 플레이어와 닿으면 상호작용 가능 (E키)
    - 상호작용 시 파티클, 사운드, 카메라 흔들림, 타입 변경 이벤트 발생
    - 랜덤 타입 부여 (플레이어 없으면 기본 타입)
    - 타입 아이콘 표시 및 힌트 UI 표시
    - AI Wander로 이동
    - 빛 효과 따라다님
    """

    def __init__(self, spawn_position: pg.Vector2):
        super().__init__("soul", pg.Rect(spawn_position, HIT_BOX_SIZE))

        # AI 세팅
        self.ai = WanderAI(self, MIN_CHANGE_TIMER, MAX_CHANGE_TIMER)

        # 좌우 뒤집기 오프셋
        self.flip_offset = FLIP_OFFSET

        # 빛 효과 생성 및 따라다닐 속도
        self.light = Light(LIGHT_SIZE, pg.Vector2(self.rect.center), LIGHT_STRENGTH)
        self.light_follow_speed = 5

        # 플레이어 상태가 없으면 기본 타입으로 설정
        if hasattr(self.scene, "player_status"):
            self.soul_type = random.choice(ALL_SOUL_TYPES)
            self.type_icon_image = ImageRenderer(
                self.app.ASSETS["ui"]["soul_icons"][self.soul_type],
                pg.Vector2(self.rect.center) + pg.Vector2(0, self.rect.h / 2),
                anchor=pg.Vector2(0.5, 0),
                use_camera=True
            )
        else:
            self.soul_type = SOUL_DEFAULT
            self.type_icon_image = None

        # 힌트 UI (E키 안내)
        self.hint_ui = TextRenderer(
            f"[E] {self.soul_type}",
            pg.Vector2(self.rect.centerx, self.rect.top - 30),
            anchor=pg.Vector2(0.5, 1.0),
            use_camera=True
        )
        self.hint_ui.alpha = 0

        # 상태 트래킹용
        self.player_was_inside = False
        self.current_tween = None

        # 상호작용 파티클 애니메이션
        self.collect_particle_anim = self.app.ASSETS["animations"]["vfxs"]["soul"]["interact"]

    def interact(self):
        """플레이어가 E키로 상호작용 했을 때 실행"""
        AnimatedParticle(self.collect_particle_anim, pg.Vector2(self.rect.center))
        self.app.sound_manager.play_sfx(self.app.ASSETS["sounds"]["soul"]["interact"])
        self.camera.shake_amount += 10

        self.scene.event_bus.emit("on_soul_interact", self.soul_type)

        # 상호작용 후 타입 랜덤 변경 및 UI 갱신
        self.soul_type = random.choice(ALL_SOUL_TYPES)
        if self.type_icon_image:
            self.type_icon_image.image = self.app.ASSETS["ui"]["soul_icons"][self.soul_type]
        self.hint_ui.text = f"[E] {self.soul_type}"

    def destroy(self):
        """소울 제거시 리소스 정리"""
        self.light.destroy()
        if self.type_icon_image:
            self.type_icon_image.destroy()
        if self.hint_ui:
            self.hint_ui.destroy()
        super().destroy()

    def follow_objects(self):
        """빛과 타입 아이콘 위치를 소울 위치로 부드럽게 따라다니게 함"""
        lerp_factor = max(min(self.app.dt * self.light_follow_speed, 1), 0)
        self.light.position = self.light.position.lerp(self.rect.center, lerp_factor)
        if self.type_icon_image:
            self.type_icon_image.pos = pg.Vector2(self.rect.center) + pg.Vector2(0, self.rect.h / 2)

    def handle_input(self):
        """플레이어가 영혼과 닿았을 때 E키 입력 감지"""
        if not hasattr(self.scene, "player_status") or not hasattr(self.scene.player_status, "player_character"):
            return
        if self.scene.player_status.health <= 0:
            return

        ps = self.scene.player_status
        pc = ps.player_character

        for event in self.app.events:
            if event.type == pg.KEYDOWN and event.key == pg.K_e:
                if self.rect.colliderect(pc.rect):
                    self.interact()

    def handle_hint_ui(self):
        """플레이어가 영혼 영역에 들어가거나 나갈 때 힌트 UI 알파 애니메이션"""
        if not hasattr(self.scene, "player_status") or not hasattr(self.scene.player_status, "player_character"):
            return

        # 힌트 UI 위치 업데이트 (영혼 위치 기준)
        self.hint_ui.pos = pg.Vector2(self.rect.centerx, self.rect.top - 30)

        ps = self.scene.player_status
        pc = ps.player_character

        is_inside = self.rect.colliderect(pc.rect)

        if is_inside and not self.player_was_inside:
            # 플레이어가 영혼 안으로 들어왔을 때
            if self.current_tween:
                self.current_tween.destroy()
            self.current_tween = Tween(self.hint_ui, "alpha", self.hint_ui.alpha, 255, 0.3)
            self.player_was_inside = True

        elif not is_inside and self.player_was_inside:
            # 플레이어가 영혼 밖으로 나갔을 때
            if self.current_tween:
                self.current_tween.destroy()
            self.current_tween = Tween(self.hint_ui, "alpha", self.hint_ui.alpha, 0, 0.3)
            self.player_was_inside = False

    def update(self):
        super().update()

        self.ai.update()

        # AI에 따라 수평 속도 설정
        self.velocity.x = self.ai.direction.x * MOVE_SPEED * 100

        self.follow_objects()
        self.handle_input()
        self.handle_hint_ui()
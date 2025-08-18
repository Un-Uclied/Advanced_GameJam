import pygame as pg

from scripts.constants import *
from scripts.camera import *
from scripts.core import *

class DamageArea(GameObject):
    """
    범위 기반 대미지 오브젝트 (낫 휘두르기)

    :param rect: 공격 범위를 나타내는 pygame.Rect
    :param damage: 이 영역에 닿은 플레이어에게 입힐 대미지
    :param duration: 이 DamageArea가 유지되는 시간 (초). None이면 무제한
    :param knockback: 넉백 벡터 (옵션)
    :param once: True면 한 번만 대미지 주고 사라짐
    :param color: 디버그용 색상
    """
    def __init__(self, 
                 rect: pg.Rect, 
                 damage: int, 
                 duration: float | None = None, 
                 knockback: pg.Vector2 | None = None,
                 once: bool = False,
                 color: pg.Color = pg.Color("red")):
        super().__init__()

        self.rect = rect
        self.damage = damage
        self.duration = duration
        self.knockback = knockback
        self.once = once
        self.color = color

        self._has_damaged = False

        if self.duration is not None:
            Timer(self.duration, self.destroy)

    def update(self):
        super().update()

        ps = self.app.scene.player_status
        pc = ps.player_character

        if self.rect.colliderect(pc.rect) and not ps.current_invincible_time > 0:
            if self.once and self._has_damaged:
                return

            ps.health -= self.damage
            self.app.scene.event_bus.emit("on_player_hurt", self.damage)
            self._has_damaged = True

            if self.knockback:
                pc.velocity += self.knockback

            if self.once:
                self.destroy()

    def draw_debug(self):
        super().draw_debug()
        pg.draw.rect(self.app.surfaces[LAYER_INTERFACE], self.color, CameraView.world_rect_to_screen_rect(self.app.scene.camera, self.rect), width=2)
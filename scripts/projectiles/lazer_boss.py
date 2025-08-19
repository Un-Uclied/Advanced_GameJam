import pygame as pg

from scripts.vfx import *
from scripts.volume import *
from scripts.ui import *
from scripts.constants import *
from scripts.utils import *
from .base import EnemyProjectile

DEFAULT_LIFE_TIME = 2

class LazerBoss(EnemyProjectile):
    """
    FiveOmega 적 탄환 클래스이긴 한데 레이저를 연출할라면 그냥 탄환을 한 방향으로 드립다 쏘면 되는거 아님? ㅋ

    Args:
        start_position (pg.Vector2): 탄환 시작 위치 (보통 적 캐릭터 위치)
        start_direction (pg.Vector2): 탄환 이동 방향 벡터
    """

    def __init__(self, start_position: pg.Vector2, start_direction: pg.Vector2):
        super().__init__("boss_lazer", start_position, start_direction, DEFAULT_LIFE_TIME,
                         destroy_on_tilemap_collision=False, destroy_on_player_collision=False, corrupt_on_attack=True)

        self.light = Light(500, self.position)

    def destroy(self):
        self.light.destroy()
        super().destroy()

    def update(self):
        super().update()

        self.light.position = self.position
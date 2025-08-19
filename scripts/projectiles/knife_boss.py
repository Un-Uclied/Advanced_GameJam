import pygame as pg

from scripts.vfx import *
from scripts.ui import *
from scripts.constants import *
from scripts.utils import *
from .base import EnemyProjectile

DEFAULT_LIFE_TIME = 2

class KnifeBoss(EnemyProjectile):
    """
    FiveOmega 칼 패턴

    Args:
        start_position (pg.Vector2): 탄환 시작 위치
        start_direction (pg.Vector2): 탄환 이동 방향 벡터
    """

    def __init__(self, start_position: pg.Vector2, start_direction: pg.Vector2):
        super().__init__("boss_knife", start_position, start_direction, DEFAULT_LIFE_TIME,
                         destroy_on_tilemap_collision=False, destroy_on_player_collision=False, corrupt_on_attack=True)
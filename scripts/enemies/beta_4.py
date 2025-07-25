import pygame as pg

from scripts.constants.app_settings import *

from .base import WanderEnemy

hit_box_size = (80, 165)

class FourBeta(WanderEnemy):
    def __init__(self, spawn_position : pg.Vector2):
        rect = pg.Rect(spawn_position, hit_box_size)
        super().__init__("four_beta", rect,
                         max_health=175,
                         attack_damage=30,
                         move_speed=5,
                         min_change_timer=.1,
                         max_change_timer=.2)

        self.flip_offset = {
            False: pg.Vector2(-20, -13),
            True: pg.Vector2(-20, -13)
        }
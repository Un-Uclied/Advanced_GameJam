import pygame as pg

from datas.const import *

from .base.wander_enemy import WanderEnemy

hit_box_size = (110, 110)

class TwoBeta(WanderEnemy):
    def __init__(self, spawn_position : pg.Vector2):
        rect = pg.Rect(spawn_position, hit_box_size)
        super().__init__(TWO_BETA, rect, 
                         attack_damage=15, 
                         move_speed=2.8, 
                         min_change_timer=1, 
                         max_change_timer=1.4)
        
        self.flip_offset = {
            False: pg.Vector2(0, -12),
            True: pg.Vector2(0, -12)
        }
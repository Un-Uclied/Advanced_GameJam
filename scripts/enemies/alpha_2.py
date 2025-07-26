import pygame as pg

from .base import ProjectileEnemy

from scripts.constants import *
from scripts.projectiles import ProjectileAlpha

hit_box_size = (110, 110)

class TwoAlpha(ProjectileEnemy):
    def __init__(self, spawn_position : pg.Vector2):
        rect = pg.Rect(spawn_position, hit_box_size)
        super().__init__("two_alpha", rect, 
                         max_health=125,
                         attack_damage=10,
                         fire_range=700,
                         projectile_damage = 15,
                         fire_cooltime=1.5,
                         projectile_class=ProjectileAlpha, 
                         move_speed=2.2, 
                         min_change_timer=.8, 
                         max_change_timer=1.8)
        
        self.flip_offset = {
            False: pg.Vector2(0, -12),
            True: pg.Vector2(0, -12)
        }
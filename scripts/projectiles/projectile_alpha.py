import pygame as pg

from .base import Projectile

projectile_speed = 400

class ProjectileAlpha(Projectile):
    def __init__(self, start_position : pg.Vector2, start_direction : pg.Vector2):
        super().__init__("enemy_projectile_alpha", start_position, start_direction, projectile_speed)
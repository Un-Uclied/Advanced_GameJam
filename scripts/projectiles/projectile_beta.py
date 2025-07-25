import pygame as pg

from .base import Projectile

projectile_speed = 500

class ProjectileBeta(Projectile):
    def __init__(self, start_position : pg.Vector2, start_direction : pg.Vector2):
        super().__init__("enemy_projectile_beta", start_position, start_direction, projectile_speed)
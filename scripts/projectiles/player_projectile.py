import pygame as pg

from .base import Projectile

from scripts.enemies import all_enemy_types
from scripts.objects import GameObject
from scripts.vfx import AnimatedParticle

class PlayerProjectile(Projectile):
    def __init__(self, start_position : pg.Vector2, start_direction : pg.Vector2):
        super().__init__("player_projectile",
                         start_position,
                         start_direction)
        
        self.app.ASSETS["sounds"]["player"]["projectile"].play()

    def destroy(self):
        AnimatedParticle("player_projectile_destroy", self.position)
        super().destroy()
        
    def update(self):
        super().update()
        all_enemies = GameObject.get_objects_by_types(all_enemy_types)
        for enemy in all_enemies:
            if enemy.rect.collidepoint(self.position):
                enemy.status.health -= self.data["damage"]
                self.destroy()
                break
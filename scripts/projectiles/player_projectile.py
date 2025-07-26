import pygame as pg

from .base import Projectile

class PlayerProjectile(Projectile):
    def __init__(self, entity_name : str, damage : int, start_position : pg.Vector2, start_direction : pg.Vector2):
        super().__init__("player",
                         entity_name,
                         damage,
                         start_position,
                         start_direction,
                         speed=700)
        
        self.app.ASSETS["sounds"]["player"]["projectile"].play()

    def on_destroy(self):
        super().on_destroy()
        from scripts.vfx import AnimatedParticle
        AnimatedParticle("player_projectile_destroy", self.position)
        
    def on_update(self):
        super().on_update()

        from scripts.enemies.base import Enemy
        for enemy in Enemy.all_enemies:
            if enemy.rect.collidepoint(self.position):
                enemy.status.health -= self.damage
                self.on_destroy()
                break
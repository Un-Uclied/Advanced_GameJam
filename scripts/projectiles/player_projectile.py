import pygame as pg

from scripts.enemies.base import Enemy

from .base import Projectile

class PlayerProjectile(Projectile):
    def __init__(self, entity_name : str, damage : int, start_position : pg.Vector2, start_direction : pg.Vector2):
        super().__init__("player_projectile",
                         entity_name,
                         damage,
                         start_position,
                         start_direction,
                         speed=700)
        
        self.app.ASSET_SFXS["player"]["projectile"].play()
        
    def on_update(self):
        super().on_update()

        for enemy in Enemy.all_enemies:
            if enemy.rect.collidepoint(self.position):
                enemy.status.health -= self.damage
                self.destroy()
        
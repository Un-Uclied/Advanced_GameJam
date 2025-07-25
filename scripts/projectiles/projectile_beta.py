import pygame as pg

from scripts.status import PlayerStatus

from .base import Projectile

class ProjectileBeta(Projectile):
    def __init__(self, entity_name : str, damage : int, start_position : pg.Vector2, start_direction : pg.Vector2):
        super().__init__("enemy_projectile_beta",
                         entity_name,
                         damage,
                         start_position,
                         start_direction,
                         speed=500)
        
        self.app.ASSET_SFXS["enemy"]["projectile"].play()
        
    def on_update(self):
        super().on_update()
        pc = self.app.scene.pc
        if pc.rect.collidepoint(self.position):
            PlayerStatus.singleton.health -= self.damage
            self.destroy()
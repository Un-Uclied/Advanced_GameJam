import pygame as pg

from .base import Projectile

from scripts.vfx import AnimatedParticle

class ProjectileBeta(Projectile):
    def __init__(self, entity_name : str, damage : int, start_position : pg.Vector2, start_direction : pg.Vector2):
        super().__init__("two_beta",
                         entity_name,
                         damage,
                         start_position,
                         start_direction,
                         speed=500)
        
        self.app.ASSETS["sounds"]["enemy"]["projectile"].play()

    
    def on_destroy(self):
        super().on_destroy()
        AnimatedParticle("enemy_beta_projectile_destroy", self.position)
        
    def on_update(self):
        super().on_update()

        from scripts.entities import PlayerCharacter
        from scripts.status import PlayerStatus

        pc = PlayerCharacter.singleton
        if pc.rect.collidepoint(self.position):
            PlayerStatus.singleton.health -= self.damage
            self.on_destroy()
import pygame as pg

from .base import Projectile

from scripts.vfx import AnimatedParticle

class ProjectileBeta(Projectile):
    def __init__(self, start_position : pg.Vector2, start_direction : pg.Vector2):
        super().__init__("two_beta_projectile",
                         start_position,
                         start_direction)
        
        #탄막 스폰시 소리 내기
        self.app.ASSETS["sounds"]["enemy"]["projectile"].play()

    def destroy(self):
        AnimatedParticle("enemy_beta_projectile_destroy", self.position)
        super().destroy()
        
    def update(self):
        super().update()

        ps = self.app.scene.player_status
        pc = ps.player_character
        if pc.rect.collidepoint(self.position):
            ps.health -= self.data["damage"]
            self.destroy()
import pygame as pg

from scripts.objects import GameObject
from scripts.vfx import AnimatedParticle

class EnemyStatus(GameObject):
    def __init__(self, entity, max_health = 100):
        super().__init__()
        self.entity = entity

        self.max_health = max_health
        self._health = self.max_health

    @property
    def health(self):
        return self._health
    
    @health.setter
    def health(self, value):
        before_health = self._health
        self._health = max(min(value, self.max_health), 0)
        if before_health > self._health:
            self.app.scene.camera.shake(before_health - self._health) 

            if self._health > 0:
                self.app.ASSET_SFXS["enemy"]["hurt"].play()
                AnimatedParticle("hurt", pg.Vector2(self.entity.rect.center))
            else:
                self.app.ASSET_SFXS["enemy"]["die"].play()
                AnimatedParticle("enemy_die", pg.Vector2(self.entity.rect.center))
            

        if self._health <= 0:
            self.entity.destroy()
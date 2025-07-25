import pygame as pg

from scripts.vfx import AnimatedParticle
from scripts.objects import GameObject

class PlayerStatus(GameObject):
    singleton : 'PlayerStatus' = None
    def __init__(self):
        super().__init__()
        PlayerStatus.singleton = self

        self.max_health = 100
        self._health = self.max_health

        self.is_invincible = False
        self.max_invincible_timer = 1.5
        self.current_invincible_timer = 0

    @property
    def health(self):
        return self._health
    
    @health.setter
    def health(self, value):
        if self.is_invincible: return

        pc = self.app.scene.pc

        before_health = self._health
        self._health = max(min(value, self.max_health), 0)
        if before_health > self._health:
            self.app.scene.camera.shake((before_health - self._health) * 2)#감소된 체력 * 2 만큼 흔들기
            self.current_invincible_timer = self.max_invincible_timer

            self.app.ASSET_SFXS["player"]["hurt"].play()
            AnimatedParticle("hurt", pg.Vector2(pc.rect.center))

        if self._health <= 0:
            self.app.change_scene("main_game_scene")

    def on_update(self):
        super().on_update()
        if self.current_invincible_timer > 0:
            self.current_invincible_timer -= self.app.dt
            self.is_invincible = True
        else:
            self.is_invincible = False

    
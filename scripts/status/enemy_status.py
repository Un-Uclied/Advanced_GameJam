import pygame as pg
import json

from scripts.vfx import AnimatedParticle

class EnemyStatus:
    def __init__(self, enemy):
        self.enemy = enemy

        with open("datas/enemy_data.json", 'r') as f:
            self.data = json.load(f)[self.enemy.name]

        self.max_health = self.data["max_health"]
        self._health = self.max_health
        self.move_speed = self.data["move_speed"]
        self.attack_damage = self.data["attack_damage"]

    @property
    def health(self):
        return self._health
    
    @health.setter
    def health(self, value):

        before_health = self._health
        self._health = max(min(value, self.max_health), 0)

        app = self.enemy.app
        camera = app.scene.camera

        if before_health > self._health:
            camera.shake_amount += before_health - self._health

            #죽을때와 체력이 깎일때 효과음 | 파티클이 다르게끔
            if self._health > 0:
                app.ASSETS["sounds"]["enemy"]["hurt"].play()
                AnimatedParticle("hurt", pg.Vector2(self.enemy.rect.center))
            else:
                app.ASSETS["sounds"]["enemy"]["die"].play()
                AnimatedParticle("enemy_die", pg.Vector2(self.enemy.rect.center))
            
        if self._health <= 0:
            self.enemy.destroy()
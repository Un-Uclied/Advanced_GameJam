import pygame as pg

from .wander_enemy import WanderEnemy

from scripts.constants import *

class ProjectileEnemy(WanderEnemy):
    def __init__(self, name : str, rect, fire_range, fire_cooltime, projectile_class, min_change_timer, max_change_timer):
        super().__init__(name, rect,
                         min_change_timer, 
                         max_change_timer)

        self.fire_range = fire_range

        self.fire_cooltime = fire_cooltime
        self.current_cooltime_timer = self.fire_cooltime

        self.projectile_class = projectile_class

    def attack(self):
        self.projectile_class(pg.Vector2(self.rect.center), pg.Vector2(1, 0) if self.flip_x else pg.Vector2(-1, 0))

    def update(self):
        super().update()

        if self.current_cooltime_timer > 0:
            self.current_cooltime_timer -= self.app.dt
        else:
            ps = self.app.scene.player_status
            pc = ps.player_character
            entity_center = pg.Vector2(self.rect.center)
            player_center = pg.Vector2(pc.rect.center)
            current_distance = entity_center.distance_to(player_center)

            if current_distance <= self.fire_range:
                self.current_cooltime_timer = self.fire_cooltime
                self.attack()
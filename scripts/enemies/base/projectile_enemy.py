import pygame as pg

from datas.const import *

from .wander_enemy import WanderEnemy

class ProjectileEnemy(WanderEnemy):
    def __init__(self, name : str, rect, max_health, attack_damage, fire_range, projectile_damage, fire_cooltime, projectile_class, move_speed, min_change_timer, max_change_timer):
        super().__init__(name, rect, 
                         max_health,
                         attack_damage,
                         move_speed, 
                         min_change_timer, 
                         max_change_timer)
        
        self.flip_offset = {
            False: pg.Vector2(0, -12),
            True: pg.Vector2(0, -12)
        }

        self.projectile_damage = projectile_damage
        self.fire_range = fire_range

        self.fire_cooltime = fire_cooltime
        self.current_cooltime_timer = self.fire_cooltime

        self.projectile_class = projectile_class

    def attack(self):
        self.projectile_class(self.name, self.projectile_damage, pg.Vector2(self.rect.center), pg.Vector2(1, 0) if self.flip_x else pg.Vector2(-1, 0))

    def on_update(self):
        super().on_update()

        if self.current_cooltime_timer > 0:
            self.current_cooltime_timer -= self.app.dt
        else:
            pc = self.app.scene.pc
            entity_center = pg.Vector2(self.rect.center)
            player_center = pg.Vector2(pc.rect.center)
            current_distance = entity_center.distance_to(player_center)

            if current_distance <= self.fire_range:
                self.current_cooltime_timer = self.fire_cooltime
                self.attack()
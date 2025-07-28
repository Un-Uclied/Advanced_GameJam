import pygame as pg

from scripts.constants import *
from scripts.entities.base import *
from scripts.vfx import Outline, AnimatedParticle

class PhysicsEnemy(PhysicsEntity):
    def __init__(self, name : str, rect : pg.Rect, collide_attack_damage : int):
        self.outline = Outline(self, "red")
        super().__init__(name, rect, invert_x=True)

        self.collide_attack_damage = collide_attack_damage
        
    def destroy(self):
        self.outline.destroy()
        super().destroy()
        
    def update(self):
        super().update()

        ps = self.app.scene.player_status
        pc = ps.player_character

        if self.rect.colliderect(pc.rect) and not ps.is_invincible:
            ps.health -= self.collide_attack_damage

            AnimatedParticle("enemy_attack", pg.Vector2(self.rect.center))
            self.app.ASSETS["sounds"]["enemy"]["attack"].play()

class ProjectileEnemy(PhysicsEnemy):
    def __init__(self, name : str, rect, collide_attack_damage : int, fire_range : float, fire_cooltime : float, projectile_class : type):
        super().__init__(name, rect, collide_attack_damage)

        self.fire_range = fire_range

        self.fire_cooltime = fire_cooltime
        self.current_cooltime_timer = self.fire_cooltime

        self.projectile_class = projectile_class

    def fire(self):
        self.projectile_class(pg.Vector2(self.rect.center), pg.Vector2(1, 0) if self.flip_x else pg.Vector2(-1, 0))

    def update_fire(self):
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
                self.fire()

    def update(self):
        super().update()
        self.update_fire()

class GhostEnemy(Entity):
    def __init__(self, name: str, rect: pg.Rect, collide_attack_damage : int, max_attack_time : float):

        self.outline = Outline(self, "red")
        super().__init__(name, rect, start_action="run", invert_x=True)

        self.collide_attack_damage = collide_attack_damage

        self.max_attack_time = max_attack_time
        self.current_attack_time = 0

        self.is_attacking = False

    def destroy(self):
        self.outline.destroy()
        super().destroy()

    def control_animation(self):
        if self.is_attacking:
            self.set_action("attack")
        else:
            self.set_action("run")

    def attack(self):
        if self.is_attacking:
            return
        self.is_attacking = True
        self.current_attack_time = self.max_attack_time

        ps = self.app.scene.player_status
        ps.health -= self.collide_attack_damage
        
        self.set_action("attack")
        AnimatedParticle("enemy_attack", pg.Vector2(self.rect.center))
        self.app.ASSETS["sounds"]["enemy"]["attack"].play()

    def update_attack(self):
        if self.current_attack_time > 0:
            self.current_attack_time -= self.app.dt
        else:
            self.is_attacking = False

    def update(self):
        super().update()

        self.update_attack()
        self.control_animation()

        ps = self.app.scene.player_status
        pc = ps.player_character
        if self.rect.colliderect(pc.rect) and not ps.is_invincible:
            self.attack()
import pygame as pg

from scripts.constants.app_settings import *

from scripts.entities.base import PhysicsEntity
from scripts.vfx import Outline, AnimatedParticle
from scripts.ai import WanderAI
from scripts.entities import PlayerCharacter
from .enemy import Enemy

from scripts.status import PlayerStatus, EnemyStatus

class WanderEnemy(PhysicsEntity):
    def __init__(self, name : str, rect : pg.Rect, max_health : int, attack_damage : int, 
                 move_speed : float,
                 min_change_timer : float, 
                 max_change_timer : float):
        
        self.outline = Outline(self, "red")
        super().__init__(name, rect, invert_x=True)

        self.ai = WanderAI(self, move_speed, min_change_timer, max_change_timer)
        self.status = EnemyStatus(self, max_health)

        self.flip_offset = {
            False: pg.Vector2(-12, -5),
            True: pg.Vector2(-12, -5)
        }

        self.attack_damage = attack_damage

        Enemy.all_enemies.append(self)

    def control_animation(self):
        if self.ai.direction.x == 0:
            self.set_action("idle")
        else:
            self.set_action("run")
        
    def on_destroy(self):
        self.outline.on_destroy()
        if self in Enemy.all_enemies:
            Enemy.all_enemies.remove(self)
        super().on_destroy()
        
    def on_update(self):
        super().on_update()
        self.ai.on_update()
        self.control_animation()

        self.velocity.x = self.ai.direction.x * self.ai.move_speed * 100

        pc = PlayerCharacter.singleton
        if self.rect.colliderect(pc.rect) and not PlayerStatus.singleton.is_invincible:
            PlayerStatus.singleton.health -= self.attack_damage

            AnimatedParticle("enemy_attack", pg.Vector2(self.rect.center))
            self.app.ASSETS["sounds"]["enemy"]["attack"].play()
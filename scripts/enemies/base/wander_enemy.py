import pygame as pg

from datas.const import *

from scripts.entities.base import PhysicsEntity
from scripts.volume.outline import Outline
from scripts.vfx import AnimatedParticle
from scripts.ai import WanderAI

from scripts.status import PlayerStatus

class WanderEnemy(PhysicsEntity):
    def __init__(self, name : str, rect : pg.Rect, attack_damage : int,
                 move_speed : float,
                 min_change_timer : float, 
                 max_change_timer : float):
        
        self.outline = Outline(self, "red")
        super().__init__(name, rect, invert_x=True)

        self.ai = WanderAI(self, move_speed, min_change_timer, max_change_timer)

        self.flip_offset = {
            False: pg.Vector2(-12, -5),
            True: pg.Vector2(-12, -5)
        }

        self.attack_damage = attack_damage

    def control_animation(self):
        if self.ai.direction.x == 0:
            self.set_action("idle")
        else:
            self.set_action("run")
        
    def destroy(self):
        super().destroy()
        self.outline.destroy()

    def on_update(self):
        super().on_update()
        self.ai.on_update()
        self.control_animation()

        self.velocity.x = self.ai.direction.x * self.ai.move_speed * 100

        pc = self.app.scene.pc
        if self.rect.colliderect(pc.rect) and not PlayerStatus.singleton.is_invincible:
            AnimatedParticle("enemy_attack", pg.Vector2(self.rect.center))
            PlayerStatus.singleton.health -= self.attack_damage
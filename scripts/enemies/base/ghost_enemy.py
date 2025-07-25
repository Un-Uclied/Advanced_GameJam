import pygame as pg

from datas.const import *

from scripts.entities.base import Entity
from scripts.volume import Outline
from scripts.vfx import AnimatedParticle
from scripts.ai import ChaseAI

from scripts.status import PlayerStatus

class GhostEnemy(Entity):
    def __init__(self, name: str, rect: pg.Rect,
                 follow_speed: float, 
                 max_follow_range: float, 
                 attack_damage : int, 
                 max_attack_time: float):
    
        self.outline = Outline(self, "red")
        super().__init__(name, rect, start_action="run", invert_x=True)

        self.ai = ChaseAI(self, follow_speed, max_follow_range)

        self.max_attack_time = max_attack_time
        self.current_attack_time = 0

        self.attack_damage = attack_damage
        self.is_attacking = False

    def attack(self):
        if self.is_attacking:
            return
        self.is_attacking = True
        self.current_attack_time = self.max_attack_time
        self.set_action("attack")
        AnimatedParticle("enemy_attack", pg.Vector2(self.rect.center))

        PlayerStatus.singleton.health -= self.attack_damage

    def update_attack(self):
        if self.current_attack_time > 0:
            self.current_attack_time -= self.app.dt
            self.ai.can_follow = False
        else:
            self.is_attacking = False
            self.ai.can_follow = True
            self.set_action("run")

    def on_update(self):
        super().on_update()
        pc = self.app.scene.pc

        if self.rect.colliderect(pc.rect):
            self.attack()

        self.update_attack()

        self.ai.on_update()
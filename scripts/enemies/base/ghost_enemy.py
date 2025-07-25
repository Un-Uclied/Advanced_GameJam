import pygame as pg

from datas.const import *

from scripts.entities.base import Entity
from scripts.vfx import Outline, AnimatedParticle
from scripts.ai import ChaseAI
from .enemy import Enemy

from scripts.status import EnemyStatus, PlayerStatus

class GhostEnemy(Entity):
    def __init__(self, name: str, rect: pg.Rect,
                 max_health : int,
                 follow_speed: float, 
                 max_follow_range: float, 
                 attack_damage : int, 
                 max_attack_time: float):
    
        self.outline = Outline(self, "red")
        super().__init__(name, rect, start_action="run", invert_x=True)

        self.ai = ChaseAI(self, follow_speed, max_follow_range)
        self.status = EnemyStatus(self, max_health)

        self.max_attack_time = max_attack_time
        self.current_attack_time = 0

        self.attack_damage = attack_damage
        self.is_attacking = False

        Enemy.all_enemies.append(self)

    def destroy(self):
        self.outline.destroy()
        Enemy.all_enemies.remove(self)
        super().destroy()

    def attack(self):
        if self.is_attacking:
            return
        self.is_attacking = True
        self.current_attack_time = self.max_attack_time

        PlayerStatus.singleton.health -= self.attack_damage

        self.set_action("attack")
        AnimatedParticle("enemy_attack", pg.Vector2(self.rect.center))
        self.app.ASSET_SFXS["enemy"]["attack"].play()

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
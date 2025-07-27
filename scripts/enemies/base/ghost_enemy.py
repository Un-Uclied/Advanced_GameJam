import pygame as pg

from scripts.constants import *
from scripts.entities.base import Entity
from scripts.vfx import Outline, AnimatedParticle
from scripts.ai import ChaseAI
from scripts.status import EnemyStatus

class GhostEnemy(Entity):
    def __init__(self, name: str, rect: pg.Rect,
                 max_follow_range: float, 
                 max_attack_time: float):

        #아웃라인 먼저 생성해야 아웃라인이 적을 덮는것을 방지
        self.outline = Outline(self, "red")
        super().__init__(name, rect, start_action="run", invert_x=True)

        self.status = EnemyStatus(self)
        self.ai = ChaseAI(self, self.status.move_speed, max_follow_range)

        self.max_attack_time = max_attack_time
        self.current_attack_time = 0

        self.is_attacking = False

    def destroy(self):
        '''생성한 아웃라인을 없애고 Enemy.all_enemies에서 자신을 없애고 destroy()'''
        self.outline.destroy()
        super().destroy()

    def attack(self):
        if self.is_attacking:
            return
        self.is_attacking = True
        self.current_attack_time = self.max_attack_time

        #체력 깎기
        ps = self.app.scene.player_status
        ps.health -= self.status.attack_damage
        
        #액션 및 효과
        self.set_action("attack")
        AnimatedParticle("enemy_attack", pg.Vector2(self.rect.center))
        self.app.ASSETS["sounds"]["enemy"]["attack"].play()

    def update_attack(self):
        if self.current_attack_time > 0:
            self.current_attack_time -= self.app.dt
            self.ai.can_follow = False
        else:
            self.is_attacking = False
            self.ai.can_follow = True
            self.set_action("run")

    def update(self):
        super().update()
        self.ai.on_update()

        ps = self.app.scene.player_status
        pc = ps.player_character

        if self.rect.colliderect(pc.rect):
            self.attack()

        self.update_attack()
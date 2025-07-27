import pygame as pg

from scripts.constants import *
from scripts.entities.base import PhysicsEntity
from scripts.vfx import Outline, AnimatedParticle
from scripts.ai import WanderAI
from scripts.status import EnemyStatus

class WanderEnemy(PhysicsEntity):
    def __init__(self, name : str, rect : pg.Rect,
                 min_change_timer : float, 
                 max_change_timer : float):
        
        #아웃라인 먼저 생성해야 아웃라인이 적을 덮는것을 방지
        self.outline = Outline(self, "red")
        super().__init__(name, rect, invert_x=True)

        self.status = EnemyStatus(self)
        self.ai = WanderAI(self, self.status.move_speed, min_change_timer, max_change_timer)

    def control_animation(self):
        if self.ai.direction.x == 0:
            self.set_action("idle")
        else:
            self.set_action("run")
        
    def destroy(self):
        '''생성한 아웃라인을 없애고 destroy()'''
        self.outline.destroy()
        super().destroy()
        
    def update(self):
        super().update()
        self.ai.on_update()
        self.control_animation()

        self.velocity.x = self.ai.direction.x * self.ai.move_speed * 100

        ps = self.app.scene.player_status
        pc = ps.player_character

        #체력 깎을때 자동으로 무적이면 안 바꾸지만 검사 안하면 겹치는 도중 계속 공격 이펙트 나옴
        if self.rect.colliderect(pc.rect) and not ps.is_invincible:
            ps.health -= self.status.attack_damage

            AnimatedParticle("enemy_attack", pg.Vector2(self.rect.center))
            self.app.ASSETS["sounds"]["enemy"]["attack"].play()
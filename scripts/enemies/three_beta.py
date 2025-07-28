import random

from scripts.constants import *
from scripts.status import EnemyStatus
from scripts.ai import ChaseAI

HIT_BOX_SIZE = (100, 100)
FLIP_OFFSET = {
    False : [0, -12],
    True  : [-4, -12]
}

MAX_HEALTH = 100

MOVE_SPEED = 3
MAX_FOLLOW_RANGE = 400

COLLIDE_ATTACK_DAMAGE = 10
MAX_ATTACK_TIME = 1.2

MIN_X_TP_RANGE = -400
MAX_X_TP_RANGE = 400
Y_TP_RANGE = -400

from .base import GhostEnemy
class ThreeBeta(GhostEnemy):
    def __init__(self, spawn_position : pg.Vector2):
        super().__init__(
                         name="three_beta",
                         rect=pg.Rect(spawn_position, HIT_BOX_SIZE),
                         collide_attack_damage=COLLIDE_ATTACK_DAMAGE,
                         max_attack_time=MAX_ATTACK_TIME)

        self.flip_offset = FLIP_OFFSET

        self.status = EnemyStatus(self, MAX_HEALTH)
        self.ai = ChaseAI(self, MAX_FOLLOW_RANGE)

    def attack(self):
        '''공격시 랜덤 위치로 텔레포트'''
        ps = self.app.scene.player_status
        pc = ps.player_character

        pc_position = pg.Vector2(pc.rect.center)
        pc_position += pg.Vector2(random.randint(MIN_X_TP_RANGE, MAX_X_TP_RANGE), random.randint(Y_TP_RANGE, 0))
        self.rect.center = pc_position
        super().attack()

    def update(self):
        super().update()
        
        self.ai.update()
        
        # 공격 애니메이션 중에는 따라가지 않게
        if self.is_attacking:
            self.movement = pg.Vector2(0, 0)
        else:
            self.movement = self.ai.direction * MOVE_SPEED * 100
    
        dt = self.app.dt
        self.rect.x += self.movement.x * dt
        self.rect.y += self.movement.y * dt
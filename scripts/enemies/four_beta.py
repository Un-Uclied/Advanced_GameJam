from scripts.constants import *
from scripts.status import EnemyStatus
from scripts.ai import WanderAI

HIT_BOX_SIZE = (100, 100)
FLIP_OFFSET = {
    False : [0, -12],
    True  : [-4, -12]
}

MAX_HEALTH = 100

MOVE_SPEED = 7
MIN_CHANGE_TIMER = 0.1
MAX_CHANGE_TIMER = 0.2

COLLIDE_ATTACK_DAMAGE = 20

from .base import PhysicsEnemy
class FourBeta(PhysicsEnemy):
    def __init__(self, spawn_position : pg.Vector2):
        super().__init__(
                         name="four_beta",
                         rect=pg.Rect(spawn_position, HIT_BOX_SIZE),
                         collide_attack_damage=COLLIDE_ATTACK_DAMAGE)

        self.flip_offset = FLIP_OFFSET

        self.status = EnemyStatus(self, MAX_HEALTH)
        self.ai = WanderAI(self, MIN_CHANGE_TIMER, MAX_CHANGE_TIMER)

    def control_animation(self):
        if self.ai.direction.x == 0:
            self.set_action("idle")
        else:
            self.set_action("run")

    def update(self):
        super().update()
        
        self.ai.update()
        self.control_animation()
        
        self.velocity.x = self.ai.direction.x * MOVE_SPEED * 100
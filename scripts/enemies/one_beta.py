from scripts.constants import *
from scripts.status import *
from scripts.ai import *
from .base import PhysicsEnemy

HIT_BOX_SIZE = (100, 100)
FLIP_OFFSET = {
    False : [0, -22],
    True  : [-4, -22]
}

MAX_HEALTH = 75

MOVE_SPEED = 3
MIN_CHANGE_TIMER = 0.3
MAX_CHANGE_TIMER = 0.9

COLLIDE_ATTACK_DAMAGE = 12

class OneBeta(PhysicsEnemy):
    def __init__(self, spawn_position : pg.Vector2):
        super().__init__(
                         name="one_beta",
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
        
        self.velocity.x = self.ai.direction.x * ((MOVE_SPEED + ENEMY_EVIL_A_SPEED_UP) if self.status.soul_type == SOUL_EVIL_A else MOVE_SPEED) * 100
from scripts.constants import *
from scripts.status import *
from scripts.ai import *
from .base import GhostEnemy

HIT_BOX_SIZE = (100, 100)
FLIP_OFFSET = {
    False : [0, -12],
    True  : [-4, -12]
}

MAX_HEALTH = 75

MOVE_SPEED = 2.2
MAX_FOLLOW_RANGE = 500

COLLIDE_ATTACK_DAMAGE = 17
ATTACK_COOLDOWN = 1

class ThreeAlpha(GhostEnemy):
    def __init__(self, spawn_position : pg.Vector2):
        super().__init__(
                         name="three_alpha",
                         rect=pg.Rect(spawn_position, HIT_BOX_SIZE),
                         collide_attack_damage=COLLIDE_ATTACK_DAMAGE,
                         attack_cool=ATTACK_COOLDOWN)

        self.flip_offset = FLIP_OFFSET

        self.status = EnemyStatus(self, MAX_HEALTH)
        self.ai = ChaseAI(self, MAX_FOLLOW_RANGE)

    def update(self):
        self.ai.update()
        self.movement = self.ai.direction * ((MOVE_SPEED + ENEMY_EVIL_A_SPEED_UP) if self.status.soul_type == SOUL_EVIL_A else MOVE_SPEED) * 100

        # 공격 애니메이션 중에는 따라가지 않게
        if not self.current_action == "attack":
            dt = self.app.dt
            self.rect.x += self.movement.x * dt
            self.rect.y += self.movement.y * dt

        super().update()
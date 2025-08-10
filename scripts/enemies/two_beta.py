from scripts.constants import *
from scripts.status import *
from scripts.ai import *
from .base import ProjectileEnemy

HIT_BOX_SIZE = (100, 100)
FLIP_OFFSET = {
    False : [0, -12],
    True  : [-4, -12]
}

MAX_HEALTH = 50

MOVE_SPEED = 2.2
MIN_CHANGE_TIMER = 0.1
MAX_CHANGE_TIMER = 0.4

COLLIDE_ATTACK_DAMAGE = 15

FIRE_RANGE = 500
FIRE_COOLTIME = 1
from scripts.projectiles import ProjectileBeta
PROJECTILE_CLASS = ProjectileBeta

class TwoBeta(ProjectileEnemy):
    def __init__(self, spawn_position : pg.Vector2):
        super().__init__(
                         name="two_beta",
                         rect=pg.Rect(spawn_position, HIT_BOX_SIZE),
                         collide_attack_damage=COLLIDE_ATTACK_DAMAGE,
                         fire_range=FIRE_RANGE,
                         fire_cooltime=FIRE_COOLTIME,
                         projectile_class=PROJECTILE_CLASS)

        self.flip_offset = FLIP_OFFSET

        self.status = EnemyStatus(self, MAX_HEALTH)
        self.ai = WanderAI(self, MIN_CHANGE_TIMER, MAX_CHANGE_TIMER)

    def _control_animation(self):
        if self.ai.direction.x == 0:
            self.set_action("idle")
        else:
            self.set_action("run")

    def update(self):
        super().update()
        
        self.ai.update()
        self._control_animation()
        
        self.velocity.x = self.ai.direction.x * ((MOVE_SPEED + ENEMY_EVIL_A_SPEED_UP) if self.status.soul_type == SOUL_EVIL_A else MOVE_SPEED) * 100
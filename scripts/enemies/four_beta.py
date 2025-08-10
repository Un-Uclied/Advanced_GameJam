from scripts.constants import *
from scripts.status import *
from scripts.ai import *
from scripts.ui import *
from .base import PhysicsEnemy

HIT_BOX_SIZE = (80, 170)
FLIP_OFFSET = {
    False : [-12, -8],
    True  : [-8, -8]
}

MAX_HEALTH = 100

MOVE_SPEED = 7
MIN_CHANGE_TIMER = 0.1
MAX_CHANGE_TIMER = 0.2

COLLIDE_ATTACK_DAMAGE = 22

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

    def do_attack(self, damage, pos, shake=0):
        super().do_attack(damage, pos, shake)
        ps = self.app.scene.player_status

        # 큐가 비어있지 않고, 전부 DEFAULT가 아닐 때만 실행
        if ps.soul_queue and not all(soul == SOUL_DEFAULT for soul in ps.soul_queue):
            for i in range(len(ps.soul_queue)):
                ps.soul_queue[i] = SOUL_DEFAULT  # 값 교체
            self.app.scene.event_bus.emit("on_player_soul_changed")
            PopupText(
                "혼이 감염되어 소멸해버렸다...",
                pg.Vector2(SCREEN_SIZE.x / 2, 680),
                fade_delay=.25,
                fade_duration=1.5
            )

    def update(self):
        super().update()
        
        self.ai.update()
        self.control_animation()
        
        self.velocity.x = self.ai.direction.x * ((MOVE_SPEED + ENEMY_EVIL_A_SPEED_UP) if self.status.soul_type == SOUL_EVIL_A else MOVE_SPEED) * 100
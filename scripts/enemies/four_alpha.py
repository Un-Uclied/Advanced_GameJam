from scripts.constants import *
from scripts.status import *
from scripts.ai import *
from scripts.ui import *
from scripts.vfx import *
from .base import PhysicsEnemy

HIT_BOX_SIZE = (80, 170)
FLIP_OFFSET = {
    False : [-12, -8],
    True  : [-8, -8]
}

MAX_HEALTH = 100

MOVE_SPEED_NORMAL = 2
MIN_CHANGE_TIMER_NORMAL = 0.8
MAX_CHANGE_TIMER_NORMAL = 1.2

CRAZY_RANGE = 350

MOVE_SPEED_CRAZY = 7
MIN_CHANGE_TIMER_CRAZY = 0.05
MAX_CHANGE_TIMER_CRAZY = 0.2

COLLIDE_ATTACK_DAMAGE = 20

class FourAlpha(PhysicsEnemy):
    def __init__(self, spawn_position : pg.Vector2):
        super().__init__(
                         name="four_alpha",
                         rect=pg.Rect(spawn_position, HIT_BOX_SIZE),
                         collide_attack_damage=COLLIDE_ATTACK_DAMAGE)

        self.flip_offset = FLIP_OFFSET

        self.status = EnemyStatus(self, MAX_HEALTH)
        self.ai = WanderAI(self, MIN_CHANGE_TIMER_NORMAL, MAX_CHANGE_TIMER_NORMAL)

        self.current_move_speed = MOVE_SPEED_NORMAL

    def _control_animation(self):
        if self.ai.direction.x == 0:
            self.set_action("idle")
        else:
            self.set_action("run")

    def do_attack(self, damage, pos, shake=0):
        super().do_attack(damage, pos, shake)
        ps = self.app.scene.player_status

        # # 무적이 아니고, 큐가 비어있지 않고, 전부 DEFAULT가 아닐 때만 실행
        if ps.current_invincible_time <= 0 and ps.soul_queue and not all(soul == SOUL_DEFAULT for soul in ps.soul_queue):
            for i in range(len(ps.soul_queue)):
                ps.soul_queue[i] = SOUL_DEFAULT  # 값 교체
            self.app.scene.event_bus.emit("on_player_soul_changed")
            AnimatedParticle(self.app.ASSETS["animations"]["vfxs"]["darkness"], pg.Vector2(ps.player_character.rect.center))
            PopupText(
                "혼이 감염되어 소멸해버렸다...",
                pg.Vector2(SCREEN_SIZE.x / 2, 680),
                fade_delay=.25,
                fade_duration=1.5
            )

    @property
    def is_player_nearby(self):
        if not hasattr(self.app.scene, "player_status") or not hasattr(self.app.scene.player_status, "player_character"):
            return False

        ps = self.app.scene.player_status
        pc = ps.player_character
        entity_center = pg.Vector2(self.rect.center)
        player_center = pg.Vector2(pc.rect.center)
        return entity_center.distance_to(player_center) < CRAZY_RANGE

    def update(self):
        super().update()
        
        self.ai.update()
        self._control_animation()

        if self.is_player_nearby:
            self.current_move_speed = MOVE_SPEED_CRAZY
            self.ai.min_change_timer = MIN_CHANGE_TIMER_CRAZY
            self.ai.max_change_timer = MAX_CHANGE_TIMER_CRAZY
        else:
            self.current_move_speed = MOVE_SPEED_NORMAL
            self.ai.min_change_timer = MIN_CHANGE_TIMER_NORMAL
            self.ai.max_change_timer = MAX_CHANGE_TIMER_NORMAL

        self.velocity.x = self.ai.direction.x * ((self.current_move_speed + ENEMY_EVIL_A_SPEED_UP) if self.status.soul_type == SOUL_EVIL_A else self.current_move_speed) * 100
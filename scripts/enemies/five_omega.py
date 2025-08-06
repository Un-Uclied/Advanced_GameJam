from scripts.constants import *
from scripts.status import *
from scripts.core import *
from scripts.ai import *
from scripts.vfx import *
from scripts.attacks import *
from .base import PhysicsEnemy

HIT_BOX_SIZE = (100, 256)
FLIP_OFFSET = {
    False : [-165, -25],
    True  : [-125, -25]
}

MAX_HEALTH = 5000

MOVE_SPEED = 3
MIN_CHANGE_TIMER = .1
MAX_CHANGE_TIMER = 1.2

COLLIDE_ATTACK_DAMAGE = 15

# 이정도로 가까이 있으면 AI의 방향 무시, 플레이어 방향으로만 감.
DIRECTION_OVERRIDE_RANGE = 400

SCYTHE_ATTACK_TRIGGER_RANGE = 220
SCYTHE_ATTACK_DAMAGE = 22
SCYTHE_ATTACK_WIDTH = 180
SCYTHE_ATTACK_COOLTIME = 1.25

class FiveOmega(PhysicsEnemy):
    def __init__(self, spawn_position: pg.Vector2):
        super().__init__(
            name="five_omega",
            rect=pg.Rect(spawn_position, HIT_BOX_SIZE),
            collide_attack_damage=COLLIDE_ATTACK_DAMAGE
        )

        self.flip_offset = FLIP_OFFSET
        self.status = EnemyStatus(self, MAX_HEALTH)
        self.ai = WanderAI(self, MIN_CHANGE_TIMER, MAX_CHANGE_TIMER)

        self.can_move = True
        self.x_direction = 0
        self.is_overriding = False

        self.player_direction = pg.Vector2(1, 0)
        self.player_distance_len = 0

        self.current_scythe_cooltime = SCYTHE_ATTACK_COOLTIME

        self.scythe_attack_sound = self.app.ASSETS["sounds"]["enemy"]["boss"]["scythe"]
        self.explosion_particle_anim = self.app.ASSETS["animations"]["vfxs"]["explosion"]

    def update(self):
        super().update()

        self.update_scythe_cooltime()
        self.update_ai()
        self.update_movement()
        self.update_attack()
        self.control_animation()

    def update_scythe_cooltime(self):
        if self.current_scythe_cooltime > 0:
            self.current_scythe_cooltime -= self.app.dt

    def update_ai(self):
        self.ai.update()

        pc = self.app.scene.player_status.player_character
        to_player = pg.Vector2(pc.rect.center) - pg.Vector2(self.rect.center)
        self.player_distance_len = to_player.length()
        self.player_direction = to_player.normalize()

        self.is_overriding = self.player_distance_len < DIRECTION_OVERRIDE_RANGE
        if self.is_overriding:
            self.x_direction = 1 if self.player_direction.x > 0 else -1
        else:
            self.x_direction = self.ai.direction.x

    def update_movement(self):
        if self.can_move:
            self.velocity.x = self.ai.direction.x * ((MOVE_SPEED + ENEMY_EVIL_A_SPEED_UP) if self.status.soul_type == SOUL_EVIL_A else MOVE_SPEED) * 100

    def update_attack(self):
        if self.player_distance_len < SCYTHE_ATTACK_TRIGGER_RANGE:
            self.try_scythe_attack()

    def try_scythe_attack(self):
        if self.current_scythe_cooltime > 0:
            return

        self.current_scythe_cooltime = SCYTHE_ATTACK_COOLTIME
        self.set_action("scythe_attack")

        self.app.scene.camera.shake_amount += 30
        self.app.sound_manager.play_sfx(self.scythe_attack_sound)

        # 낫 이펙트
        side_pos = self.rect.topleft if self.x_direction < 0 else self.rect.center
        AnimatedParticle(self.explosion_particle_anim, pg.Vector2(side_pos))

        damage_rect = self.rect.copy()
        damage_rect.w = SCYTHE_ATTACK_WIDTH
        damage_rect.x += self.rect.w if self.x_direction > 0 else -SCYTHE_ATTACK_WIDTH
        DamageArea(damage_rect, SCYTHE_ATTACK_DAMAGE, .45, once=False)

        # 움직임 멈췄다가 0.85초 뒤 다시 움직이게
        self.can_move = False
        Timer(0.85, lambda: setattr(self, "can_move", True))

    def control_animation(self):
        if self.can_move:
            if self.is_overriding or self.ai.direction.x != 0:
                self.set_action("run")
            else:
                self.set_action("idle")
import pygame as pg

from scripts.camera import *
from scripts.projectiles import *
from scripts.volume import *
from .base import PhysicsEntity, VELOCITY_DRAG

HIT_BOX_SIZE = (48, 128)
FLIP_OFFSET = {
    False : pg.Vector2(0, 0),
    True : pg.Vector2(-40, 0)
}

MOVE_SPEED = 3.8
JUMP_POWER = -7.5

MAX_JUMP_COUNT = 2

ACCEL_POWER = 7
DECCEL_POWER = 5
PLAYER_PROJECTILE_KNOCKBACK = 400

CAMERA_FOLLOW_SPEED = 5

LIGHT_SIZE = 500

class PlayerCharacter(PhysicsEntity):
    def __init__(self, spawn_position : pg.Vector2):
        super().__init__("player", pg.Rect(spawn_position, HIT_BOX_SIZE))

        self.input_drection = pg.Vector2()

        # 현재 점프한 횟수
        self.current_jump_count = 0

        #가속 속도와 감속 속도를 다르게 하기 위해
        self.is_accel = False

        self.lerped_movement = pg.Vector2()

        self.flip_offset = FLIP_OFFSET

    def handle_input(self):
        '''인풋 핸들'''
        # 움직임은 한번 눌리는게 아니라 "눌려있는것을" 가져와야해서 pg.KEYDOWN방식이 아니라 pg.key.get_pressed()를 사용함.
        key = pg.key.get_pressed()
        self.input_drection = pg.Vector2()
        if key[pg.K_a]:
            self.input_drection.x = -1
        if key[pg.K_d]:
            self.input_drection.x = 1
        if key[pg.K_w]:
            self.input_drection.y = 1
        if key[pg.K_s]:
            self.input_drection.y = -1

        # 가속
        self.is_accel = bool(self.input_drection.x)
        
        for event in self.app.events:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    # 점프
                    self.jump()

            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # 탄환 공격
                    self.projectile_attack()

    def control_animation(self):
        '''애니메이션 조절'''
        if not self.collisions["down"]:
            self.set_action("jump")
        else:
            if self.is_accel:
                self.set_action("run")
            else : self.set_action("idle")

    def projectile_attack(self):
        '''탄환 공격'''
        camera = self.app.scene.camera

        # 마우스 위치 (스크린 좌표계)를 월드 좌표계로 변환후 방향 계산
        plr_pos = pg.Vector2(self.rect.center)
        direction = (CameraMath.screen_to_world(camera, pg.Vector2(pg.mouse.get_pos())) - plr_pos).normalize()
        PlayerProjectile(plr_pos, direction)

        self.velocity += -pg.Vector2(direction.x, 0) * PLAYER_PROJECTILE_KNOCKBACK  # 탄환 발사시 플레이어가 밀려나도록 (y축은 무시)

    def jump(self):
        '''점프 시도'''
        if (self.current_jump_count >= MAX_JUMP_COUNT): return
        self.current_gravity = JUMP_POWER * 100
        self.current_jump_count += 1

        # 플레이어 점프 소리 재생
        self.app.sound_manager.play_sfx(self.app.ASSETS["sounds"]["player"]["jump"])

    def physics_gravity(self):
        super().physics_gravity()

        # 바닥에 있을시 현재 점프한 횟수 0으로 초기화
        if self.collisions["down"]:
            self.current_jump_count = 0

    def physics_movement(self):
        # super().physics_movement() | super().physics_movement()는 움직임이 플레이어 인풋 계산 까지 포함 안되서 안 부름.

        self.lerped_movement = self.lerped_movement.lerp(
            pg.Vector2(self.input_drection.x * MOVE_SPEED * 100, 0),
            max(min((ACCEL_POWER if self.is_accel else DECCEL_POWER) * self.app.dt, 1), 0)
        )

        # velocity + 중력 + 인풋에 따른 움직임량 을 더한것이 움직임량
        self.movement = pg.Vector2(self.velocity.x + self.lerped_movement.x, self.velocity.y + self.current_gravity)

        # velocity 감쇠
        self.velocity = self.velocity.lerp(pg.Vector2(0, 0), max(min(self.app.dt * VELOCITY_DRAG, 1), 0))

    def follow_light_and_camera(self):
        '''카메라랑 빛 위치 업데이트'''
        camera = self.app.scene.camera
        target_pos = self.rect.center

        camera.position = camera.position.lerp(target_pos, max(min(self.app.dt * CAMERA_FOLLOW_SPEED, 1), 0))

    def update(self):
        self.handle_input()

        super().update()

        # 플레이어는 인풋 방향에만 따라 좌우 반전하게 함. (그래야 예쁨)
        if self.input_drection.x < 0:
            self.anim.flip_x = not self.invert_x
        elif self.input_drection.x > 0:
            self.anim.flip_x = self.invert_x

        self.control_animation()
        self.follow_light_and_camera()
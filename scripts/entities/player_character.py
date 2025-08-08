import pygame as pg

from scripts.constants import *
from scripts.camera import *
from scripts.projectiles import *
from scripts.volume import *
from .base import PhysicsEntity, VELOCITY_DRAG

HIT_BOX_SIZE = (48, 100)
FLIP_OFFSET = {
    False : pg.Vector2(-70, -39),
    True : pg.Vector2(-70, -39)
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

        self.view_direction = "right"
        self.input_drection = pg.Vector2()

        # 현재 점프한 횟수
        self.current_jump_count = 0

        #가속 속도와 감속 속도를 다르게 하기 위해
        self.is_accel = False

        self.lerped_movement = pg.Vector2()

        self.flip_offset = FLIP_OFFSET

        # 이벤트 등록
        self.app.scene.event_bus.connect("on_player_soul_changed", lambda: self.set_action("change_soul"))
        self.app.scene.event_bus.connect("on_player_died", lambda: self.set_action("die"))

        def on_player_invincible(started):
            if started:
                self.set_action("hurt")

        self.app.scene.event_bus.connect("on_player_invincible", on_player_invincible)

    def handle_input(self):
        '''인풋 핸들'''
        
        # 죽으면 인풋 안받음
        ps = self.app.scene.player_status
        if ps.health <= 0:
            return
        
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

        # 애니메이션 방향
        if self.input_drection.x > 0:
            self.view_direction = "right"
        elif self.input_drection.x < 0:
            self.view_direction = "left"

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
        ACTION_PRIORITY = ("change_soul", "hurt", "attack", "die")
        ps = self.app.scene.player_status

        # 우선순위 액션 처리
        if self.current_action in ACTION_PRIORITY and not self.anim.done:
            return  # 현재 우선순위 액션이 끝나지 않았으면 유지
        # 죽으면 애니메이션 업뎃 안함
        if ps.health <= 0:
            return

        # 바닥에 있음
        if self.collisions["down"]:
            if self.is_accel:
                if SOUL_KIND_C in ps.soul_queue:
                    self.set_action("rush")
                else:
                    self.set_action("run")
            else:
                self.set_action("idle")
        # 공중에 있음
        else:
            if self.current_gravity > 0:
                self.set_action("jump")
            elif self.current_gravity < 0:
                self.set_action("fall")

    def projectile_attack(self):
        '''탄환 공격'''
        ps = self.app.scene.player_status
        attack_cooltime = ps.attack_cooltime
        # 공격 쿨타임 중이면 리턴
        if attack_cooltime.current_time > 0: 
            return
        # 공격 쿨타임 초기화
        attack_cooltime.reset()

        camera = self.app.scene.camera
        # 마우스 위치 (스크린 좌표계)를 월드 좌표계로 변환후 방향 계산
        plr_pos = pg.Vector2(self.rect.center)
        direction = (CameraMath.screen_to_world(camera, pg.Vector2(pg.mouse.get_pos())) - plr_pos).normalize()
        PlayerProjectile(plr_pos, direction)

        # SOUL_EVIL_A가지고 있다면 넉백 증가
        nuckback = PLAYER_PROJECTILE_KNOCKBACK
        if SOUL_EVIL_A in ps.soul_queue:
            nuckback += EVIL_A_NUCK_BACK_UP
        self.velocity += -pg.Vector2(direction.x, 0) * nuckback  # 탄환 발사시 플레이어가 밀려나도록 (y축은 무시)

        # 애니메이션
        self.set_action("attack")
        if direction.x < 0:
            self.view_direction = "left"
        elif direction.x > 0:
            self.view_direction = "right"

    def jump(self):
        '''점프 시도'''
        # 최대 점프 횟수 계산
        max_jump_count = MAX_JUMP_COUNT
        ps = self.app.scene.player_status
        if SOUL_EVIL_C in ps.soul_queue:
            max_jump_count += 1

        if (self.current_jump_count >= max_jump_count):
            return
        
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

        move_speed = MOVE_SPEED

        # 영혼 타입에 맞게 이동속도 맞추기
        ps = self.app.scene.player_status
        if SOUL_KIND_A in ps.soul_queue:
            move_speed -= KIND_A_SPEED_DOWN
        if SOUL_KIND_C in ps.soul_queue:
            move_speed += KIND_C_SPEED_UP

        self.lerped_movement = self.lerped_movement.lerp(
            pg.Vector2(self.input_drection.x * move_speed * 100, 0),
            max(min((ACCEL_POWER if self.is_accel else DECCEL_POWER) * self.app.dt, 1), 0)
        ) if ps.health > 0 else pg.Vector2(0, 0) # 죽으면 못움직임

        # velocity + 중력 + 인풋에 따른 움직임량 을 더한것이 움직임량
        self.movement = pg.Vector2(self.velocity.x + self.lerped_movement.x, self.velocity.y + self.current_gravity)

        # velocity 감쇠
        self.velocity = self.velocity.lerp(pg.Vector2(0, 0), max(min(self.app.dt * VELOCITY_DRAG, 1), 0))

    def follow_light_and_camera(self):
        '''카메라랑 빛 위치 업데이트'''
        camera = self.app.scene.camera
        target_pos = self.rect.center

        camera.position = camera.position.lerp(target_pos, max(min(self.app.dt * CAMERA_FOLLOW_SPEED, 1), 0))

    def flip_anim(self):
        super().flip_anim() # 왜 인지는 모르겠는데 얘가 없으면 키 떼는 순간 계속 False가 됨;; 어이 없넹;
        # 플레이어 캐릭터는 움직이는 방향이 아니라 오로지 인풋 방향으로만 flip함. (이유 : 오른쪽으로 가다가 왼쪽으로 넉백된다고 왼쪽을 바라보게 되면 안 예쁨.)
        if self.view_direction == "left":
            self.anim.flip_x = not self.invert_x
        else:
            self.anim.flip_x = self.invert_x

    def update(self):
        self.handle_input()
        self.control_animation()
        super().update()
        self.follow_light_and_camera()
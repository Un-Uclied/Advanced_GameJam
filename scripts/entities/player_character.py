import pygame as pg

from scripts.constants import *
from scripts.camera import *
from scripts.projectiles import *
from scripts.core import *
from scripts.ui import *
from scripts.volume import *
from .base import PhysicsEntity, VELOCITY_DRAG, MAX_GRAVITY

HIT_BOX_SIZE = (48, 100)
FLIP_OFFSET = {
    False: pg.Vector2(-70, -39),
    True: pg.Vector2(-70, -39),
}

FALL_WARNING_TIME = 3

MOVE_SPEED = 3.8
JUMP_POWER = -7.5
MAX_JUMP_COUNT = 2

ACCEL_POWER = 7
DECCEL_POWER = 5
PLAYER_PROJECTILE_KNOCKBACK = 400

DASH_COOLTIME = 1
DASH_POWER = 1000
DASH_INVINCIBLE_TIME = .45
DASH_GRAVITY_TIME = .15
DASH_COST = 150

CAMERA_FOLLOW_SPEED = 5
LIGHT_SIZE = 500

class PlayerCharacter(PhysicsEntity):
    """
    플레이어 캐릭터 엔티티 클래스
    
    - 물리 기반 이동 및 중력 처리 상속
    - 입력 처리, 점프, 공격, 애니메이션 관리
    - 카메라 및 빛 위치 업데이트
    """

    def __init__(self, spawn_position: pg.Vector2):
        super().__init__("player", pg.Rect(spawn_position, HIT_BOX_SIZE))

        self.view_direction = "right"   # 현재 바라보는 방향 ("left" 또는 "right")
        self.input_direction = pg.Vector2()  # 키 입력 방향 벡터

        self.current_jump_count = 0     # 현재 점프 횟수 추적
        self.is_accel = False           # 가속 중인지 여부

        self.lerped_movement = pg.Vector2()  # 부드러운 움직임 보간용

        self.flip_offset = FLIP_OFFSET

        # 낙하 경고용 타이머 (일시정지 메뉴 안내 팝업)
        self.fall_timer = Timer(
            FALL_WARNING_TIME,
            lambda: PopupText("일시정지 메뉴에서 재시작", pg.Vector2(SCREEN_SIZE.x / 2, 670), 0.5)
        )
        self.fall_timer.active = False

        # 대쉬 쿨타임용 타이머
        self.dash_timer = Timer(
            DASH_COOLTIME, None, auto_destroy=False
        )
        self.is_dashing = False

        # 이벤트 등록
        self.app.scene.event_bus.connect("on_player_soul_changed", lambda: self.set_action("change_soul"))
        self.app.scene.event_bus.connect("on_player_died", lambda: self.set_action("die"))
        self.app.scene.event_bus.connect("on_player_hurt", self._on_player_hurt)

    def get_direction_from(self, point : pg.Vector2):
        '''적이 부르는 헬퍼 function (적과 플레이어의 방향을 줌)'''
        to_plr_dir = pg.Vector2(self.rect.center) - pg.Vector2(point)

        if to_plr_dir.length_squared() == 0:
            return pg.Vector2(0, 0)
        else:
            return to_plr_dir.normalize()
        
    def get_distance_from(self, point : pg.Vector2):
        '''적이 부르는 헬퍼 function (적과 플레이어의 거리를 줌)'''
        to_plr_dir = pg.Vector2(self.rect.center) - pg.Vector2(point)
        return to_plr_dir.length()

    def _on_player_hurt(self, _damage):
        ps = self.app.scene.player_status
        if ps.health <= 0:
            return
        if ps.current_invincible_time > 0:
            return
        self.set_action("hurt")

    def _handle_input(self):
        """플레이어 키보드 & 마우스 입력 처리"""

        ps = self.app.scene.player_status
        if ps.health <= 0:
            return  # 죽었으면 입력 무시

        keys = pg.key.get_pressed()
        self.input_direction = pg.Vector2()

        if keys[pg.K_a]:
            self.input_direction.x = -1
        if keys[pg.K_d]:
            self.input_direction.x = 1
        if keys[pg.K_w]:
            self.input_direction.y = 1
        if keys[pg.K_s]:
            self.input_direction.y = -1

        # 바라보는 방향 업데이트
        if self.input_direction.x > 0:
            self.view_direction = "right"
        elif self.input_direction.x < 0:
            self.view_direction = "left"

        self.is_accel = bool(self.input_direction.x)

        # 이벤트 루프에서 점프 및 공격 처리
        for event in self.app.events:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self._jump()
                if event.key == pg.K_LSHIFT:
                    self._dash()
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                self._projectile_attack()

    def _control_animation(self):
        """
        애니메이션 상태 관리
        
        우선순위 액션 유지, 상태에 따른 애니메이션 변경 처리
        """
        ACTION_PRIORITY = ("change_soul", "hurt", "attack", "die")
        ps = self.app.scene.player_status

        # 우선순위 액션 중이면 애니메이션 유지
        if self.current_action in ACTION_PRIORITY and not self.anim.done:
            return
        if ps.health <= 0:  # 죽었으면 애니메이션 업데이트 안함
            return

        if self.collisions["down"]:  # 바닥에 있을 때
            if self.is_accel:
                if SOUL_KIND_C in ps.soul_queue:
                    self.set_action("rush")
                else:
                    self.set_action("run")
            else:
                self.set_action("idle")
        else:  # 공중에 있을 때
            if self.current_gravity > 0:
                self.set_action("jump")
            elif self.current_gravity < 0:
                self.set_action("fall")

    def _projectile_attack(self):
        """탄환 발사 처리"""

        ps = self.app.scene.player_status
        attack_cooltime = ps.attack_cooltime
        if attack_cooltime.current_time > 0:
            return  # 쿨타임 중이면 공격 불가
        attack_cooltime.reset()

        camera = self.app.scene.camera
        player_pos = pg.Vector2(self.rect.center)
        mouse_pos = pg.Vector2(pg.mouse.get_pos())
        direction = (CameraMath.screen_to_world(camera, mouse_pos) - player_pos)
        if direction.length_squared() != 0:
            direction.normalize_ip()

        PlayerProjectile(player_pos, direction)

        # 넉백 효과
        knockback = PLAYER_PROJECTILE_KNOCKBACK
        if SOUL_EVIL_A in ps.soul_queue:
            knockback += EVIL_A_NUCK_BACK_UP

        self.velocity += -pg.Vector2(direction.x, 0) * knockback  # y축 넉백은 무시

        # 공격 애니메이션과 바라보는 방향 설정
        self.set_action("attack")
        self.view_direction = "left" if direction.x < 0 else "right"

    def _dash(self):
        '''대쉬 시도, 실행'''
        # 가만히 있다면 대쉬 안함
        if self.input_direction.x == 0:
            return
        # 대쉬 쿨타임이 아직 안됐다면 대쉬 안함
        if self.dash_timer.current_time > 0:
            return
        # 쿨타임 초기화
        self.dash_timer.reset()
        # 상태 설정
        self.is_dashing = True
        # 힘 주기
        self.velocity.x += self.input_direction.x * DASH_POWER
        # 중력 0으로 초기화
        self.current_gravity = 0

        ps = self.app.scene.player_status
        ps.current_invincible_time += DASH_INVINCIBLE_TIME
        self.app.scene.score -= DASH_COST
        
        self.app.sound_manager.play_sfx(self.app.ASSETS["sounds"]["player"]["dash"])
        Timer(DASH_GRAVITY_TIME, lambda: setattr(self, "is_dashing", False))

    def _jump(self):
        """점프 시도"""

        ps = self.app.scene.player_status
        max_jumps = MAX_JUMP_COUNT + (1 if SOUL_EVIL_C in ps.soul_queue else 0)

        if self.current_jump_count >= max_jumps:
            return  # 점프 횟수 초과

        self.current_gravity = JUMP_POWER * 100
        self.current_jump_count += 1

        self.app.sound_manager.play_sfx(self.app.ASSETS["sounds"]["player"]["jump"])

    def _physics_gravity(self):
        """중력 처리 및 점프 횟수 초기화"""

        # 대쉬 중이면 중력 안함
        if not self.is_dashing:
            super()._physics_gravity()

        if self.collisions["down"]:
            self.current_jump_count = 0

    def _physics_movement(self):
        """
        움직임 계산
        
        - 플레이어 인풋에 따라 부드럽게 움직임 lerp 적용
        - velocity + 중력 + lerped movement 합산해서 최종 movement 설정
        """

        ps = self.app.scene.player_status

        move_speed = MOVE_SPEED
        if SOUL_KIND_A in ps.soul_queue:
            move_speed -= KIND_A_SPEED_DOWN
        if SOUL_KIND_C in ps.soul_queue:
            move_speed += KIND_C_SPEED_UP

        accel = ACCEL_POWER if self.is_accel else DECCEL_POWER
        dt = self.app.dt

        self.lerped_movement = self.lerped_movement.lerp(
            pg.Vector2(self.input_direction.x * move_speed * 100, 0),
            max(min(accel * dt, 1), 0)
        ) if ps.health > 0 else pg.Vector2(0, 0)

        self.movement = pg.Vector2(self.velocity.x + self.lerped_movement.x, self.velocity.y + self.current_gravity)

        self.velocity = self.velocity.lerp(pg.Vector2(0, 0), max(min(dt * VELOCITY_DRAG, 1), 0))

    def _follow_light_and_camera(self):
        """카메라 및 빛 위치 부드럽게 따라가기"""

        camera = self.app.scene.camera
        target_pos = self.rect.center
        dt = self.app.dt

        camera.position = camera.position.lerp(target_pos, max(min(dt * CAMERA_FOLLOW_SPEED, 1), 0))

    def _flip_anim(self):
        """
        애니메이션 좌우 반전 처리
        
        - 기본 flip 처리 후, 인풋 방향에 맞게 강제 설정
        """
        super()._flip_anim()
        self.anim.flip_x = not self.invert_x if self.view_direction == "left" else self.invert_x

    def _update_fall_timer(self):
        """낙하 타이머 업데이트 (땅에 없으면 타이머 활성화)"""

        if self.collisions["down"]:
            self.fall_timer.reset()
            self.fall_timer.active = False
        else:
            self.fall_timer.active = True

    def update(self):
        """매 프레임 실행"""

        self._handle_input()
        self._control_animation()
        super().update()
        self._follow_light_and_camera()
        self._update_fall_timer()
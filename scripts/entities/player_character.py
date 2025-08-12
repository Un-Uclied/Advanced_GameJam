import pygame as pg
from scripts.constants import *
from scripts.camera import *
from scripts.projectiles import *
from scripts.core import *
from scripts.ui import *
from scripts.volume import *
from .base import PhysicsEntity, VELOCITY_DRAG, MAX_GRAVITY

# Constants
HIT_BOX_SIZE = (48, 100)
FLIP_OFFSET = {False: pg.Vector2(-70, -39), True: pg.Vector2(-70, -39)}
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

class PlayerInput:
    """플레이어 입력 처리를 담당하는 클래스"""
    
    def __init__(self, player):
        self.player = player
        self.direction = pg.Vector2()
        
    def update(self):
        """입력 처리 및 방향 업데이트"""
        if self.player.app.transition or self.player.app.scene.player_status.health <= 0:
            return
            
        self._handle_keyboard_input()
        self._handle_events()
        
    def _handle_keyboard_input(self):
        """키보드 입력 처리"""
        keys = pg.key.get_pressed()
        self.direction = pg.Vector2()
        
        if keys[pg.K_a]: self.direction.x = -1
        if keys[pg.K_d]: self.direction.x = 1
        if keys[pg.K_w]: self.direction.y = 1
        if keys[pg.K_s]: self.direction.y = -1
        
        # 바라보는 방향 업데이트
        if self.direction.x > 0:
            self.player.view_direction = "right"
        elif self.direction.x < 0:
            self.player.view_direction = "left"
            
    def _handle_events(self):
        """이벤트 처리 (점프, 대시, 공격)"""
        for event in self.player.app.events:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.abilities.jump()
                elif event.key == pg.K_LSHIFT:
                    self.player.abilities.dash()
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                self.player.abilities.attack()

class PlayerAbilities:
    """플레이어 능력 (점프, 대시, 공격) 관리 클래스"""
    
    def __init__(self, player):
        self.player = player
        self.current_jump_count = 0
        self.is_dashing = False
        self.dash_timer = Timer(DASH_COOLTIME, None, auto_destroy=False)
        
    def jump(self):
        """점프 실행"""
        ps = self.player.app.scene.player_status
        max_jumps = MAX_JUMP_COUNT + (1 if SOUL_EVIL_C in ps.soul_queue else 0)
        
        if self.current_jump_count >= max_jumps:
            return
            
        self.player.current_gravity = JUMP_POWER * 100
        self.current_jump_count += 1
        self.player.app.sound_manager.play_sfx(self.player.app.ASSETS["sounds"]["player"]["jump"])
        
    def dash(self):
        """대시 실행"""
        input_dir = self.player.input_handler.direction
        
        if input_dir.x == 0 or self.dash_timer.current_time > 0:
            return
            
        self.dash_timer.reset()
        self.is_dashing = True
        
        self.player.velocity.x += input_dir.x * DASH_POWER
        self.player.current_gravity = 0
        
        ps = self.player.app.scene.player_status
        ps.current_invincible_time += DASH_INVINCIBLE_TIME
        self.player.app.scene.score -= DASH_COST
        
        self.player.app.sound_manager.play_sfx(self.player.app.ASSETS["sounds"]["player"]["dash"])
        Timer(DASH_GRAVITY_TIME, lambda: setattr(self, "is_dashing", False))
        
    def attack(self):
        """공격 실행"""
        ps = self.player.app.scene.player_status
        if ps.attack_cooltime.current_time > 0:
            return
            
        ps.attack_cooltime.reset()
        
        # 탄환 발사
        camera = self.player.app.scene.camera
        player_pos = pg.Vector2(self.player.rect.center)
        mouse_pos = pg.Vector2(pg.mouse.get_pos())
        direction = (CameraMath.screen_to_world(camera, mouse_pos) - player_pos)
        
        if direction.length_squared() != 0:
            direction.normalize_ip()
            
        PlayerProjectile(player_pos, direction)
        
        # 넉백 효과
        knockback = PLAYER_PROJECTILE_KNOCKBACK
        if SOUL_EVIL_A in ps.soul_queue:
            knockback += EVIL_A_NUCK_BACK_UP
            
        self.player.velocity += -pg.Vector2(direction.x, 0) * knockback
        
        # 애니메이션과 방향 설정
        self.player.set_action("attack")
        self.player.view_direction = "left" if direction.x < 0 else "right"
        
    def reset_jump_count_if_grounded(self):
        """바닥에 닿았을 때 점프 횟수 초기화"""
        if self.player.collisions["down"]:
            self.current_jump_count = 0

class PlayerAnimationController:
    """플레이어 애니메이션 제어 클래스"""
    
    ACTION_PRIORITY = ("change_soul", "hurt", "attack", "die")
    
    def __init__(self, player):
        self.player = player
        
    def update(self):
        """애니메이션 상태 업데이트"""
        ps = self.player.app.scene.player_status
        
        # 우선순위 액션이나 사망 상태면 애니메이션 유지
        if (self.player.current_action in self.ACTION_PRIORITY and not self.player.anim.done) or ps.health <= 0:
            return
            
        input_dir = self.player.input_handler.direction
        is_accel = bool(input_dir.x)
        
        if self.player.collisions["down"]:  # 바닥에 있을 때
            if is_accel:
                action = "rush" if SOUL_KIND_C in ps.soul_queue else "run"
                self.player.set_action(action)
            else:
                self.player.set_action("idle")
        else:  # 공중에 있을 때
            if self.player.current_gravity > 0:
                self.player.set_action("jump")
            elif self.player.current_gravity < 0:
                self.player.set_action("fall")

class PlayerMovement:
    """플레이어 이동 처리 클래스"""
    
    def __init__(self, player):
        self.player = player
        self.lerped_movement = pg.Vector2()
        
    def update(self):
        """이동 계산 및 적용"""
        ps = self.player.app.scene.player_status
        input_dir = self.player.input_handler.direction
        
        # 속도 계산
        move_speed = self._get_modified_move_speed(ps)
        is_accel = bool(input_dir.x)
        accel = ACCEL_POWER if is_accel else DECCEL_POWER
        dt = self.player.app.dt
        
        # 부드러운 이동
        target_movement = pg.Vector2(input_dir.x * move_speed * 100, 0) if ps.health > 0 else pg.Vector2(0, 0)
        self.lerped_movement = self.lerped_movement.lerp(target_movement, max(min(accel * dt, 1), 0))
        
        # 최종 이동량 계산
        self.player.movement = pg.Vector2(
            self.player.velocity.x + self.lerped_movement.x,
            self.player.velocity.y + self.player.current_gravity
        )
        
        # 속도 감소
        self.player.velocity = self.player.velocity.lerp(pg.Vector2(0, 0), max(min(dt * VELOCITY_DRAG, 1), 0))
        
    def _get_modified_move_speed(self, ps):
        """소울에 따른 이동속도 수정"""
        move_speed = MOVE_SPEED
        if SOUL_KIND_A in ps.soul_queue:
            move_speed -= KIND_A_SPEED_DOWN
        if SOUL_KIND_C in ps.soul_queue:
            move_speed += KIND_C_SPEED_UP
        return move_speed

class PlayerCharacter(PhysicsEntity):
    """
    플레이어 캐릭터 엔티티 클래스
    
    - 물리 기반 이동 및 중력 처리 상속
    - 입력, 능력, 애니메이션, 이동을 각각 분리된 클래스로 관리
    - 카메라 및 빛 위치 업데이트
    """

    def __init__(self, spawn_position: pg.Vector2):
        super().__init__("player", pg.Rect(spawn_position, HIT_BOX_SIZE))
        
        self.view_direction = "right"
        self.flip_offset = FLIP_OFFSET
        
        # 컴포넌트 초기화
        self.input_handler = PlayerInput(self)
        self.abilities = PlayerAbilities(self)
        self.animation_controller = PlayerAnimationController(self)
        self.movement_controller = PlayerMovement(self)
        
        # 낙하 경고 타이머
        self.fall_timer = Timer(
            FALL_WARNING_TIME,
            lambda: PopupText("일시정지 메뉴에서 재시작", pg.Vector2(SCREEN_SIZE.x / 2, 670), 0.5)
        )
        self.fall_timer.active = False
        
        # 이벤트 등록
        self._register_events()
        
    def _register_events(self):
        """이벤트 등록"""
        event_bus = self.app.scene.event_bus
        event_bus.connect("on_player_soul_changed", lambda: self.set_action("change_soul"))
        event_bus.connect("on_player_died", lambda: self.set_action("die"))
        event_bus.connect("on_player_hurt", self.on_player_hurt)

    def get_direction_from(self, point: pg.Vector2):
        """적이 사용하는 헬퍼 함수 (적과 플레이어의 방향)"""
        to_plr_dir = pg.Vector2(self.rect.center) - pg.Vector2(point)
        return to_plr_dir.normalize() if to_plr_dir.length_squared() > 0 else pg.Vector2(0, 0)
        
    def get_distance_from(self, point: pg.Vector2):
        """적이 사용하는 헬퍼 함수 (적과 플레이어의 거리)"""
        to_plr_dir = pg.Vector2(self.rect.center) - pg.Vector2(point)
        return to_plr_dir.length()

    def on_player_hurt(self, _damage):
        """플레이어 피해 처리"""
        ps = self.app.scene.player_status
        if ps.health <= 0 or ps.current_invincible_time > 0:
            return
        self.set_action("hurt")

    def physics_gravity(self):
        """중력 처리 (대시 중에는 중력 무시)"""
        if not self.abilities.is_dashing:
            super().physics_gravity()
        self.abilities.reset_jump_count_if_grounded()

    def physics_movement(self):
        """물리 이동 처리"""
        self.movement_controller.update()

    def follow_light_and_camera(self):
        """카메라 부드럽게 따라가기"""
        camera = self.app.scene.camera
        target_pos = self.rect.center
        dt = self.app.dt
        camera.position = camera.position.lerp(target_pos, max(min(dt * CAMERA_FOLLOW_SPEED, 1), 0))

    def flip_anim(self):
        """애니메이션 좌우 반전 처리"""
        super().flip_anim()
        self.anim.flip_x = not self.invert_x if self.view_direction == "left" else self.invert_x

    def update_fall_timer(self):
        """낙하 타이머 업데이트"""
        if self.collisions["down"]:
            self.fall_timer.reset()
            self.fall_timer.active = False
        else:
            self.fall_timer.active = True

    def update(self):
        """매 프레임 실행"""
        self.input_handler.update()
        self.animation_controller.update()
        super().update()
        self.follow_light_and_camera()
        self.update_fall_timer()
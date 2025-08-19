import pygame as pg
from scripts.constants import *
from scripts.camera import *
from scripts.projectiles import *
from scripts.utils import *
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

class InputProcessor:
    """
    키보드 및 마우스 입력 처리 전담 클래스
    
    - 키보드 상태 감지 및 방향 벡터 계산
    - 이벤트 기반 액션 트리거 (점프, 대시, 공격)
    - 플레이어 상태에 따른 입력 무시 처리
    - 현재 인풋 방향의 y값은 사용되지 않음.
    """
    
    def __init__(self, player):
        self.player = player
        self.direction = pg.Vector2()
        
    def process_input(self):
        """전체 입력 처리 메인 함수"""
        if self.should_ignore_input():
            self.direction = pg.Vector2()
            return
            
        self.process_keyboard_state()
        self.process_input_events()
        
    def should_ignore_input(self):
        """입력을 무시해야 하는 상황인지 판단"""
        return (self.player.app.transition or 
                self.player.scene.player_status.health <= 0)
        
    def process_keyboard_state(self):
        """키보드 상태 기반 연속 입력 처리 (이동 방향)"""
        keys = pg.key.get_pressed()
        self.direction = pg.Vector2()
        
        if keys[pg.K_a]: self.direction.x = -1
        if keys[pg.K_d]: self.direction.x = 1
        if keys[pg.K_w]: self.direction.y = 1
        if keys[pg.K_s]: self.direction.y = -1
        
        self.update_view_direction()
            
    def process_input_events(self):
        """이벤트 기반 일회성 입력 처리 (점프, 대시, 공격)"""
        for event in self.player.app.events:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.action_executor.execute_jump()
                elif event.key == pg.K_LSHIFT:
                    self.player.action_executor.execute_dash()
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                self.player.action_executor.execute_attack()
    
    def update_view_direction(self):
        """입력 방향에 따른 시야 방향 업데이트"""
        if self.direction.x > 0:
            self.player.view_direction = "right"
        elif self.direction.x < 0:
            self.player.view_direction = "left"

class JumpController:
    """
    점프 기능 전담 클래스
    
    - 점프 횟수 추적 및 제한 검사
    - 소울에 따른 점프 횟수 보정
    - 착지 시 점프 횟수 초기화
    """
    
    def __init__(self, player):
        self.player = player
        self.current_jump_count = 0
        
    def can_jump(self):
        """점프 가능 여부 검사"""
        ps = self.player.scene.player_status
        max_jumps = MAX_JUMP_COUNT + (1 if SOUL_EVIL_C in ps.soul_queue else 0)
        return self.current_jump_count < max_jumps
        
    def execute_jump(self):
        """점프 실행"""
        if not self.can_jump():
            return False
            
        self.player.current_gravity = JUMP_POWER * 100
        self.current_jump_count += 1
        self.player.app.sound_manager.play_sfx(self.player.app.ASSETS["sounds"]["player"]["jump"])
        return True
        
    def reset_if_grounded(self):
        """바닥에 닿았을 때 점프 횟수 초기화"""
        if self.player.collisions["down"]:
            self.current_jump_count = 0

class DashController:
    """
    대시 기능 전담 클래스
    
    - 대시 쿨타임 관리
    - 대시 실행 및 물리 효과 적용
    - 대시 중 무적 시간 및 중력 제어
    """
    
    def __init__(self, player):
        self.player = player
        self.is_dashing = False
        self.dash_timer = Timer(DASH_COOLTIME, None, auto_destroy=False)
        
    def can_dash(self, input_direction):
        """대시 가능 여부 검사"""
        return (input_direction.x != 0 and 
                self.dash_timer.get_time() <= 0)
        
    def execute_dash(self, input_direction):
        """대시 실행"""
        if not self.can_dash(input_direction):
            return False
            
        self.dash_timer.reset()
        self.is_dashing = True
        
        # 물리 효과 적용
        self.player.velocity.x += input_direction.x * DASH_POWER
        self.player.current_gravity = 0
        
        # 플레이어 상태 업데이트
        ps = self.player.scene.player_status
        ps.current_invincible_time += DASH_INVINCIBLE_TIME
        self.player.scene.score -= DASH_COST
        
        # 사운드 및 타이머 설정
        self.player.app.sound_manager.play_sfx(self.player.app.ASSETS["sounds"]["player"]["dash"])
        Timer(DASH_GRAVITY_TIME, lambda: setattr(self, "is_dashing", False))
        return True

class AttackController:
    """
    공격 기능 전담 클래스
    
    - 공격 쿨타임 검사
    - 마우스 위치 기반 방향 계산
    - 탄환 발사 및 넉백 효과 적용
    """
    
    def __init__(self, player):
        self.player = player
        
    def can_attack(self):
        """공격 가능 여부 검사"""
        ps = self.player.scene.player_status
        return ps.attack_cooltime.get_time() <= 0
        
    def execute_attack(self):
        """공격 실행"""
        if not self.can_attack():
            return False
            
        # 쿨타임 초기화
        ps = self.player.scene.player_status
        ps.attack_cooltime.reset()
        
        # 공격 방향 계산
        direction = self.calculate_attack_direction()
        if direction.length_squared() == 0:
            return False
            
        # 탄환 발사
        PlayerProjectile(pg.Vector2(self.player.rect.center), direction)
        
        # 넉백 및 애니메이션 적용
        self.apply_knockback_effect(direction)
        self.update_attack_animation(direction)
        return True
        
    def calculate_attack_direction(self):
        """마우스 위치 기반 공격 방향 계산"""
        camera = self.player.scene.camera
        player_pos = pg.Vector2(self.player.rect.center)
        mouse_pos = pg.Vector2(pg.mouse.get_pos())
        direction = CameraMath.screen_to_world(camera, mouse_pos) - player_pos
        
        if direction.length_squared() != 0:
            direction.normalize_ip()
        return direction
        
    def apply_knockback_effect(self, direction):
        """공격 시 넉백 효과 적용"""
        ps = self.player.scene.player_status
        knockback = PLAYER_PROJECTILE_KNOCKBACK
        
        if SOUL_EVIL_A in ps.soul_queue:
            knockback += EVIL_A_NUCK_BACK_UP
            
        self.player.velocity += -pg.Vector2(direction.x, 0) * knockback
        
    def update_attack_animation(self, direction):
        """공격 애니메이션 및 바라보는 방향 설정"""
        self.player.set_action("attack")
        self.player.view_direction = "left" if direction.x < 0 else "right"

class PlayerActionExecutor:
    """
    플레이어 액션들을 조합하여 실행하는 클래스
    
    - 각 액션 컨트롤러들을 조합하여 통합 인터페이스 제공
    - 액션 실행 결과를 통합 관리
    """
    
    def __init__(self, player):
        self.player = player
        self.jump_controller = JumpController(player)
        self.dash_controller = DashController(player)
        self.attack_controller = AttackController(player)
        
    def execute_jump(self):
        """점프 액션 실행"""
        return self.jump_controller.execute_jump()
        
    def execute_dash(self):
        """대시 액션 실행"""
        input_dir = self.player.input_processor.direction
        return self.dash_controller.execute_dash(input_dir)
        
    def execute_attack(self):
        """공격 액션 실행"""
        return self.attack_controller.execute_attack()
        
    def reset_jump_if_grounded(self):
        """착지 시 점프 상태 초기화"""
        self.jump_controller.reset_if_grounded()
        
    def is_dashing(self):
        """대시 중인지 여부 반환"""
        return self.dash_controller.is_dashing

class AnimationStateMachine:
    """
    애니메이션 상태 머신 클래스
    
    - 우선순위 기반 애니메이션 상태 관리
    - 플레이어 상태 및 입력에 따른 애니메이션 전환
    - 지상/공중 상태별 애니메이션 분기 처리
    """
    
    ACTION_PRIORITY = ("change_soul", "hurt", "attack", "die")
    
    def __init__(self, player):
        self.player = player
        
    def update_animation_state(self):
        """현재 상태에 맞는 애니메이션으로 전환"""
        if self.should_maintain_current_action():
            return
            
        if self.player.collisions["down"]:
            self.set_ground_animation()
        else:
            self.set_air_animation()
            
    def should_maintain_current_action(self):
        """현재 액션을 유지해야 하는지 판단"""
        ps = self.player.scene.player_status
        return ((self.player.current_action in self.ACTION_PRIORITY and not self.player.anim.done) or 
                ps.health <= 0)
                
    def set_ground_animation(self):
        """지상에서의 애니메이션 설정"""
        input_dir = self.player.input_processor.direction
        is_moving = bool(input_dir.x)
        
        if is_moving:
            ps = self.player.scene.player_status
            action = "rush" if SOUL_KIND_C in ps.soul_queue else "run"
            self.player.set_action(action)
        else:
            self.player.set_action("idle")
            
    def set_air_animation(self):
        """공중에서의 애니메이션 설정"""
        if self.player.current_gravity > 0:
            self.player.set_action("jump")
        elif self.player.current_gravity < 0:
            self.player.set_action("fall")

class MovementCalculator:
    """
    플레이어 이동 계산 전담 클래스
    
    - 소울에 따른 이동속도 보정
    - 부드러운 이동을 위한 lerp 계산
    - 속도 및 중력을 합산한 최종 이동량 산출
    """
    
    def __init__(self, player):
        self.player = player
        self.lerped_movement = pg.Vector2()
        
    def calculate_movement(self):
        """이동량 계산 및 적용"""
        ps = self.player.scene.player_status
        input_dir = self.player.input_processor.direction
        
        move_speed = self.get_modified_move_speed(ps)
        target_movement = self.calculate_target_movement(input_dir, move_speed, ps)
        self.update_lerped_movement(target_movement, input_dir)
        self.apply_final_movement()
        self.apply_velocity_drag()
        
    def get_modified_move_speed(self, player_status):
        """소울에 따른 이동속도 보정"""
        move_speed = MOVE_SPEED
        if SOUL_KIND_A in player_status.soul_queue:
            move_speed -= KIND_A_SPEED_DOWN
        if SOUL_KIND_C in player_status.soul_queue:
            move_speed += KIND_C_SPEED_UP
        return move_speed
        
    def calculate_target_movement(self, input_dir, move_speed, player_status):
        """목표 이동량 계산"""
        if player_status.health <= 0:
            return pg.Vector2(0, 0)
        return pg.Vector2(input_dir.x * move_speed * 100, 0)
        
    def update_lerped_movement(self, target_movement, input_dir):
        """부드러운 이동을 위한 lerp 업데이트"""
        is_accelerating = bool(input_dir.x)
        accel = ACCEL_POWER if is_accelerating else DECCEL_POWER
        dt = self.player.app.dt
        
        self.lerped_movement = self.lerped_movement.lerp(
            target_movement, 
            max(min(accel * dt, 1), 0)
        )
        
    def apply_final_movement(self):
        """최종 이동량을 플레이어에 적용"""
        self.player.movement = pg.Vector2(
            self.player.velocity.x + self.lerped_movement.x,
            self.player.velocity.y + self.player.current_gravity
        )
        
    def apply_velocity_drag(self):
        """속도 감쇠 적용"""
        dt = self.player.app.dt
        self.player.velocity = self.player.velocity.lerp(
            pg.Vector2(0, 0), 
            max(min(dt * VELOCITY_DRAG, 1), 0)
        )

class CameraController:
    """
    카메라 추적 전담 클래스
    
    - 플레이어 위치를 부드럽게 따라가는 카메라 제어
    - 카메라 이동 속도 및 보간 처리
    """
    
    def __init__(self, player):
        self.player = player
        
    def update_camera_position(self):
        """카메라 위치를 플레이어 위치로 부드럽게 이동"""
        camera = self.player.scene.camera
        target_pos = self.player.rect.center
        dt = self.player.app.dt
        
        camera.position = camera.position.lerp(
            target_pos, 
            max(min(dt * CAMERA_FOLLOW_SPEED, 1), 0)
        )

class FallWarningSystem:
    """
    낙하 경고 시스템 전담 클래스
    
    - 플레이어가 공중에 있을 때 낙하 시간 추적
    - 일정 시간 후 재시작 안내 팝업 표시
    """
    
    def __init__(self, player):
        self.player = player
        self.fall_timer = Timer(
            FALL_WARNING_TIME,
            lambda: PopupText("일시정지 메뉴에서 재시작", pg.Vector2(SCREEN_SIZE.x / 2, 670), 0.5)
        )
        self.fall_timer.active = False
        
    def update_fall_status(self):
        """낙하 상태 업데이트 및 타이머 제어"""
        if self.player.collisions["down"]:
            self.fall_timer.reset()
            self.fall_timer.active = False
        else:
            self.fall_timer.active = True

class PlayerEventHandler:
    """
    플레이어 관련 이벤트 처리 전담 클래스
    
    - 게임 이벤트 등록 및 콜백 처리
    - 소울 변경, 사망, 피해 이벤트 대응
    """
    
    def __init__(self, player):
        self.player = player
        self.register_events()
        
    def register_events(self):
        """이벤트 버스에 플레이어 이벤트 등록"""
        event_bus = self.player.scene.event_bus
        event_bus.connect("on_player_soul_changed", self.on_soul_changed)
        event_bus.connect("on_player_died", self.on_player_died)
        event_bus.connect("on_player_hurt", self.on_player_hurt)
        
    def on_soul_changed(self):
        """소울 변경 시 애니메이션 처리"""
        self.player.set_action("change_soul")
        
    def on_player_died(self):
        """플레이어 사망 시 애니메이션 처리"""
        self.player.set_action("die")
        
    def on_player_hurt(self, damage):
        """플레이어 피해 시 애니메이션 처리"""
        ps = self.player.scene.player_status
        if ps.health <= 0 or ps.current_invincible_time > 0:
            return
        self.player.set_action("hurt")

class PlayerCharacter(PhysicsEntity):
    """
    플레이어 캐릭터 엔티티 클래스
    
    - 물리 기반 이동 및 중력 처리 상속
    - 각 기능별 전담 클래스들을 조합하여 플레이어 동작 구현
    - 컴포넌트 기반 아키텍처로 기능별 분리 및 조합
    
    주요 컴포넌트:
    - InputProcessor: 입력 처리
    - PlayerActionExecutor: 액션 실행 조합
    - AnimationStateMachine: 애니메이션 상태 관리
    - MovementCalculator: 이동 계산
    - CameraController: 카메라 제어
    - FallWarningSystem: 낙하 경고
    - PlayerEventHandler: 이벤트 처리
    """

    def __init__(self, spawn_position: pg.Vector2):
        super().__init__("player", pg.Rect(spawn_position, HIT_BOX_SIZE))
        
        # 기본 속성 초기화
        self.view_direction = "right"
        self.flip_offset = FLIP_OFFSET
        
        # 컴포넌트 시스템 초기화
        self.init_components()
        
    def init_components(self):
        """모든 컴포넌트 초기화 및 의존성 설정"""
        # 기본 컴포넌트들
        self.input_processor = InputProcessor(self)
        self.action_executor = PlayerActionExecutor(self)
        self.animation_state_machine = AnimationStateMachine(self)
        self.movement_calculator = MovementCalculator(self)
        self.camera_controller = CameraController(self)
        self.fall_warning_system = FallWarningSystem(self)
        self.event_handler = PlayerEventHandler(self)

    def get_direction_from(self, point: pg.Vector2):
        """
        적이 사용하는 헬퍼 메소드 (적과 플레이어의 방향 벡터 반환)
        
        Args:
            point (pg.Vector2): 기준점 위치
            
        Returns:
            pg.Vector2: 정규화된 방향 벡터
        """
        to_plr_dir = pg.Vector2(self.rect.center) - pg.Vector2(point)
        return to_plr_dir.normalize() if to_plr_dir.length_squared() > 0 else pg.Vector2(0, 0)
        
    def get_distance_from(self, point: pg.Vector2):
        """
        적이 사용하는 헬퍼 메소드 (적과 플레이어의 거리 반환)
        
        Args:
            point (pg.Vector2): 기준점 위치
            
        Returns:
            float: 플레이어와의 거리
        """
        to_plr_dir = pg.Vector2(self.rect.center) - pg.Vector2(point)
        return to_plr_dir.length()

    def physics_gravity(self):
        """물리 중력 처리 (대시 중에는 중력 무시)"""
        if not self.action_executor.is_dashing():
            super().physics_gravity()
        self.action_executor.reset_jump_if_grounded()

    def physics_movement(self):
        """물리 이동 처리 (MovementCalculator에 위임)"""
        self.movement_calculator.calculate_movement()

    def flip_anim(self):
        """애니메이션 좌우 반전 처리"""
        super().flip_anim()
        self.anim.flip_x = not self.invert_x if self.view_direction == "left" else self.invert_x

    def update(self):
        """
        매 프레임 실행되는 메인 업데이트 루프
        
        실행 순서:
        1. 입력 처리
        2. 애니메이션 상태 업데이트  
        3. 물리 업데이트 (부모 클래스)
        4. 카메라 업데이트
        5. 낙하 경고 업데이트
        """
        self.input_processor.process_input()
        self.animation_state_machine.update_animation_state()
        super().update()
        self.camera_controller.update_camera_position()
        self.fall_warning_system.update_fall_status()
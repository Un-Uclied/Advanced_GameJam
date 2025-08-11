import pygame as pg
import random

FIX_DIRECTION_TIMER = 0.6  # 충돌/떨어짐 감지 후 방향 고정 시간 (초)

class WanderAI:
    '''
    걍 가만히 왔다갔다 하는 AI임.  
    GameObject 상속 안함. 엔티티가 직접 update에서 update() 호출해줘야 함.

    :param entity: AI 적용할 엔티티 (영혼, 적 등)
    :param min_change_timer: 방향 바꾸는 랜덤 최소 시간 (초)
    :param max_change_timer: 방향 바꾸는 랜덤 최대 시간 (초)
    '''

    def __init__(self, entity, min_change_timer: float, max_change_timer: float):
        self.entity = entity
        self.direction = pg.Vector2(0, 0)
        self.direction.x = random.choice([-1, 0, 1])  # 초기 방향 랜덤 좌/정지/우
        self.direction.y = 0

        self.min_change_timer = min_change_timer
        self.max_change_timer = max_change_timer
        self.current_change_timer = random.uniform(min_change_timer, max_change_timer)

        self.fix_direction_timer = 0  # 충돌 감지 후 방향 고정 남은 시간 (초)

    def check_floor(self):
        '''내 위치 왼쪽 아래/오른쪽 아래 타일 없으면 떨어짐으로 판단, 방향 전환'''
        entity = self.entity
        tilemap = entity.app.scene.tilemap
        tile_size = tilemap.tile_size
        check_w = 4

        left_check = pg.Vector2(entity.rect.midbottom[0] - tile_size // 2 + check_w, entity.rect.bottom + 1)
        right_check = pg.Vector2(entity.rect.midbottom[0] + tile_size // 2 - check_w, entity.rect.bottom + 1)

        # 왼쪽 바닥 없으면 오른쪽으로 방향 고정
        if not any(r.collidepoint(left_check) for r in tilemap.physic_tiles_around(left_check)):
            self.handle_collision_or_fall("fall_left")

        # 오른쪽 바닥 없으면 왼쪽으로 방향 고정
        elif not any(r.collidepoint(right_check) for r in tilemap.physic_tiles_around(right_check)):
            self.handle_collision_or_fall("fall_right")

    def check_wall(self):
        '''왼쪽, 오른쪽 벽에 부딪히면 방향 고정'''
        entity = self.entity
        if entity.collisions.get("right", False):
            self.handle_collision_or_fall("hit_right")
        elif entity.collisions.get("left", False):
            self.handle_collision_or_fall("hit_left")

    def update(self):
        '''AI 메인 업데이트, 충돌/떨어짐 체크 + 방향 전환 타이머 관리'''
        self.check_floor()
        self.check_wall()

        dt = self.entity.app.dt

        if self.fix_direction_timer > 0:
            self.fix_direction_timer -= dt
            # 고정 시간 중이므로 방향 바꾸기 안 함
        else:
            # 고정 시간이 끝나면 방향 바꿀 수 있음
            if self.current_change_timer > 0:
                self.current_change_timer -= dt
            else:
                self.current_change_timer = random.uniform(self.min_change_timer, self.max_change_timer)
                self.direction.x = random.choice([-1, 0, 1])  # 새 방향 랜덤 결정

    def handle_collision_or_fall(self, event_type):
        '''충돌 혹은 바닥 없는 이벤트 들어오면 방향 강제 변경'''
        if event_type in ("fall_left", "hit_left"):
            self.direction.x = 1  # 오른쪽으로 이동
        elif event_type in ("fall_right", "hit_right"):
            self.direction.x = -1  # 왼쪽으로 이동
        self.fix_direction_timer = FIX_DIRECTION_TIMER  # 방향 고정 타이머 시작


class ChaseAI:
    '''
    플레이어 쫓아가는 AI임.  
    일정 범위 안에 플레이어 들어오면 플레이어 방향, 아니면 시작 위치 방향.

    GameObject 상속 안 함, 엔티티가 update에서 update() 직접 호출해야 함.

    :param entity: AI 적용 대상 적 엔티티
    :param max_follow_range: 플레이어를 감지하는 최대 거리 (픽셀)
    '''

    def __init__(self, entity, max_follow_range: float):
        self.entity = entity
        self.direction = pg.Vector2(0, 0)
        self.max_follow_range = max_follow_range

        self.start_position = pg.Vector2(self.entity.rect.center)
        self.target_position = self.start_position  # 목표 위치 초기화

    def update(self):
        entity = self.entity

        # 씬에 플레이어 상태 없으면 그냥 리턴 (예: 메인 메뉴)
        if not hasattr(entity.app.scene, "player_status"):
            return

        ps = entity.app.scene.player_status
        pc = ps.player_character

        entity_center = pg.Vector2(entity.rect.center)
        player_center = pg.Vector2(pc.rect.center)
        distance = entity_center.distance_to(player_center)

        # 플레이어가 감지 범위 안에 있으면 플레이어 추적, 아니면 시작 위치 복귀
        if distance <= self.max_follow_range:
            self.target_position = player_center
        else:
            self.target_position = self.start_position

        # 방향 벡터 계산 및 정규화 (길이 0인 경우 예외처리)
        self.direction = self.target_position - entity_center
        if self.direction.length_squared() > 0:
            self.direction.normalize_ip()
        else:
            self.direction = pg.Vector2(0, 0)
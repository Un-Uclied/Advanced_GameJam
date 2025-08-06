import pygame as pg
import random

# 예: 왼쪽에 충돌되거나 떨어진다고 판단될때 오른쪽으로 0.6초 가게 고정
FIX_DIRECTION_TIMER = 0.6

class WanderAI:
    '''
    이 AI는 GameObject를 상속받지 않아서 엔티티가 직접 업데이트 해야함
    그냥 왔다 갔다 가만히 있는 AI
    AI관련 클래스는 방향만 알려주는거고, 직접 위치 업데이트는 엔티티가 직접
    
    :param entity: 영혼이나 적 엔티티 인스턴스
    :param min_change_timer: 랜덤으로 방향전환하는데 랜덤의 가장 작은값
    :param max_change_timer: 랜덤으로 방향전환하는데 랜덤의 가장 큰값
    '''

    def __init__(self, entity, min_change_timer: float, max_change_timer: float):
        self.entity = entity
        self.direction = pg.Vector2()

        self.direction.x = random.choice([-1, 0, 1])
        self.direction.y = 0

        self.min_change_timer = min_change_timer
        self.max_change_timer = max_change_timer
        self.current_change_timer = random.uniform(self.min_change_timer, self.max_change_timer)

        self.fix_direction_timer = 0
    
    def check_floor(self):
        '''내 위치의 왼쪽 아래, 오른쪽 아래 탐지'''
        entity = self.entity
        tilemap = entity.app.scene.tilemap
        tile_size = tilemap.tile_size
        check_w = 4

        left = pg.Vector2(entity.rect.midbottom[0] - tile_size // 2 + check_w, entity.rect.bottom + 1)
        right = pg.Vector2(entity.rect.midbottom[0] + tile_size // 2 - check_w, entity.rect.bottom + 1)

        # r.collidepoint(left) for r in tilemap.physic_tiles_around(left) 중 하나도 충돌이 안나면 떨어질것으로 판정
        if not any(r.collidepoint(left) for r in tilemap.physic_tiles_around(left)):
            self.handle_collision_or_fall("fall_left")
        # r.collidepoint(right) for r in tilemap.physic_tiles_around(right) 중 하나도 충돌이 안나면 떨어질것으로 판정
        elif not any(r.collidepoint(right) for r in tilemap.physic_tiles_around(right)):
            self.handle_collision_or_fall("fall_right")

    def check_wall(self):
        '''왼쪽|오른쪽 충돌하면 바로 핸들로 돌리기'''
        entity = self.entity
        if entity.collisions["right"]:
            self.handle_collision_or_fall("hit_right")
        elif entity.collisions["left"]:
            self.handle_collision_or_fall("hit_left")

    def update(self):   
        self.check_floor()
        self.check_wall()

        dt = self.entity.app.dt
        if self.fix_direction_timer > 0:
            self.fix_direction_timer -= dt
        else:
            if self.current_change_timer > 0:
                self.current_change_timer -= dt
            else:
                self.current_change_timer = random.uniform(self.min_change_timer, self.max_change_timer)
                # direction이 0이면 가만히 있기
                self.direction.x = random.choice([-1, 0, 1])

    def handle_collision_or_fall(self, event_type):
        if event_type == "fall_left":
            self.direction.x = 1
        elif event_type == "fall_right":
            self.direction.x = -1
        elif event_type == "hit_left":
            self.direction.x = 1
        elif event_type == "hit_right":
            self.direction.x = -1
        self.fix_direction_timer = FIX_DIRECTION_TIMER

class ChaseAI:
    '''
    이 AI는 GameObject를 상속받지 않아서 엔티티가 직접 업데이트 해야함
    엔티티 일정거리 안으로 들어오면 self.direction이 플레이어 방향으로, 일정거리 밖이면 시작 위치로 방향을 잡음
    AI관련 클래스는 방향만 알려주는거고, 직접 위치 업데이트는 엔티티가 직접
    
    :param entity: 유령 적 엔티티 인스턴스
    :param max_follow_range: 적이 감지할수 있는 방향 (플레이어의 거리가 이 값안으로 들어오면 플레이어쪽으로 방향가고,\n 값 밖으로 나가면 다시 스폰 위치로 감)
    '''

    def __init__(self, entity, max_follow_range: float):
        
        self.entity = entity
        self.direction = pg.Vector2()

        self.max_follow_range = max_follow_range

        self.start_positon = pg.Vector2(self.entity.rect.center)
        self.target_position = self.start_positon

    def update(self):
        entity = self.entity
        
        ps = entity.app.scene.player_status
        pc = ps.player_character

        entity_center = pg.Vector2(entity.rect.center)
        player_center = pg.Vector2(pc.rect.center)
        current_distance = entity_center.distance_to(player_center)

        # 타겟 위치 설정
        if current_distance <= self.max_follow_range:
            self.target_position = player_center
        else:
            self.target_position = self.start_positon

        # 방향 계산
        self.direction = self.target_position - entity_center
        if self.direction.length_squared() > 0: # 길이가 0인 벡터 정규화 할려고 하면 에러나서 길이가 0 넘으면 정규화
            self.direction = self.direction.normalize() 
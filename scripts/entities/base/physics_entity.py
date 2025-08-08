import pygame as pg

from .entity import Entity

# 땅에 닿고 있을때의 중력
DEFAULT_GRAVITY = 300
# 최대 중력 (최대 중력 속도)
MAX_GRAVITY = 5000
# 이만큼 지속적으로 아래로 가려함
GRAVITY_STRENGTH = 28

# velocity 감쇠량
VELOCITY_DRAG = 5

class PhysicsEntity(Entity):
    '''거의 모든 엔티티의 부모 클래스'''
    def __init__(self, name, rect : pg.Rect, start_action : str = "idle", invert_x : bool = False):
        super().__init__(name, rect, start_action, invert_x)

        # 현재 닿고 있는곳
        self.collisions = {"left" : False, "right" : False, "up" : False, "down" : False}

        self.velocity : pg.Vector2 = pg.Vector2()

        self.current_gravity = DEFAULT_GRAVITY

    def physics_collision(self):
        '''진짜 움직임을 구현, 충돌도 적용'''
        self.collisions = {"left" : False, "right" : False, "up" : False, "down" : False}

        # 여기서 movement.x만큼 rect를 직접 움직임.
        self.rect.x += int(self.movement.x * self.app.dt)
        # 내 히트박스의 꼭짓점 마다
        for point in self.get_frect_points():
            # 꼭짓점 주변 타일맵의 충돌가능한 rect들 갖고오고 
            for rect in self.app.scene.tilemap.physic_tiles_around(point):
                # 충돌하고 있는데
                if rect.colliderect(self.rect):
                    # 오른쪽으로 가려고 한다면 막기
                    if (self.movement.x > 0):
                        self.collisions["right"] = True
                        self.movement.x = 0
                        self.rect.right = rect.x
                    # 왼쪽으로 가려고 한다면 막기
                    if (self.movement.x < 0):
                        self.collisions["left"] = True
                        self.movement.x = 0
                        self.rect.x = rect.right

        # 여기서 movement.y만큼 rect를 직접 움직임.
        self.rect.y += int(self.movement.y * self.app.dt)
        # 내 히트박스의 꼭짓점 마다
        for point in self.get_frect_points():
            for rect in self.app.scene.tilemap.physic_tiles_around(point):
                # 꼭짓점 주변 타일맵의 충돌가능한 rect들 갖고오고 
                if rect.colliderect(self.rect):
                    # 오른쪽으로 가려고 한다면 막기
                    if (self.movement.y > 0):
                        self.collisions["down"] = True
                        # self.movement.y = 0   수직 관련 움직임은 중력이 조절하는게 많기 때문에 주석 처리
                        self.rect.bottom = rect.y
                    # 왼쪽으로 가려고 한다면 막기
                    if (self.movement.y < 0):
                        self.collisions["up"] = True
                        # self.movement.y = 0   수직 관련 움직임은 중력이 조절하는게 많기 때문에 주석 처리
                        self.rect.top = rect.bottom
                    
    def physics_gravity(self):   
        if (self.collisions["down"]):
            # 땅을 밟고 있다면 기본 중력으로 고정
            self.current_gravity = DEFAULT_GRAVITY
        else:
            # 땅을 밟고 있지 않다면 중력량 증가
            self.current_gravity = min(MAX_GRAVITY * self.app.dt * 100, self.current_gravity + GRAVITY_STRENGTH * self.app.dt * 100)
        
        if (self.collisions["up"]):
            # 머리를 박으면 바로 0으로 바꿈
            self.current_gravity = 0

    def physics_movement(self):
        '''movement 계산'''

        # velocity + 중력을 더한것이 움직임량
        self.movement = pg.Vector2(self.velocity.x, self.velocity.y + self.current_gravity)  

        # velocity 감쇠
        self.velocity = self.velocity.lerp(pg.Vector2(0, 0), max(min(self.app.dt * VELOCITY_DRAG, 1), 0))

    def update(self):
        self.physics_movement()
        self.physics_collision()
        self.physics_gravity()
        super().update()
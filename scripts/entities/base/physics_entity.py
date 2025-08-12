import pygame as pg

from .entity import Entity

# 중력과 감쇠 관련 상수들
DEFAULT_GRAVITY = 200          # 땅에 닿았을 때 적용되는 기본 중력값
MAX_GRAVITY = 5000             # 중력 최대치 (속도 제한용)
GRAVITY_STRENGTH = 28          # 중력이 점진적으로 강해지는 양

VELOCITY_DRAG = 5              # 속도 감쇠 비율

class PhysicsEntity(Entity):
    """
    거의 모든 물리 기반 엔티티의 부모 클래스
    
    중력, 충돌, 속도 등을 처리하며,
    실제 움직임과 타일맵 충돌 판정을 구현함
    
    Attributes:
        collisions (dict): 각 방향별 충돌 상태 (left, right, up, down)
        velocity (pg.Vector2): 현재 속도 벡터
        current_gravity (float): 현재 중력값 (시간에 따라 증가 가능)
    """

    def __init__(self, name, rect: pg.Rect, start_action: str = "idle", invert_x: bool = False):
        super().__init__(name, rect, start_action, invert_x)

        self.collisions = {"left": False, "right": False, "up": False, "down": False}
        self.velocity: pg.Vector2 = pg.Vector2()
        self.current_gravity = DEFAULT_GRAVITY

    def physics_collision(self):
        """
        실제 움직임 적용 및 타일맵 충돌 판정
        
        - 수평 이동 후 충돌 검사 및 충돌 시 이동 제한
        - 수직 이동 후 충돌 검사 및 충돌 시 이동 제한 (중력 관련 부분은 따로 처리)
        """
        self.collisions = {"left": False, "right": False, "up": False, "down": False}

        # 수평 이동 적용
        self.rect.x += int(self.movement.x * self.app.dt)

        # 각 꼭짓점 주변 타일들과 충돌 체크
        for point in self.get_rect_points():
            for rect in self.app.scene.tilemap.physic_tiles_around(point):
                if rect.colliderect(self.rect):
                    if self.movement.x > 0:  # 오른쪽 이동 중 충돌
                        self.collisions["right"] = True
                        self.movement.x = 0
                        self.rect.right = rect.x
                    elif self.movement.x < 0:  # 왼쪽 이동 중 충돌
                        self.collisions["left"] = True
                        self.movement.x = 0
                        self.rect.x = rect.right

        # 수직 이동 적용
        self.rect.y += int(self.movement.y * self.app.dt)

        # 각 꼭짓점 주변 타일들과 충돌 체크
        for point in self.get_rect_points():
            for rect in self.app.scene.tilemap.physic_tiles_around(point):
                if rect.colliderect(self.rect):
                    if self.movement.y > 0:  # 아래쪽 이동 중 충돌 (땅)
                        self.collisions["down"] = True
                        # 중력 처리 따로 하기 때문에 movement.y = 0 은 하지 않음
                        self.rect.bottom = rect.y
                    elif self.movement.y < 0:  # 위쪽 이동 중 충돌 (머리 박음)
                        self.collisions["up"] = True
                        # 중력 처리 따로 하기 때문에 movement.y = 0 은 하지 않음
                        self.rect.top = rect.bottom

    def physics_gravity(self):
        """
        중력 처리
        
        - 땅에 닿아있으면 중력값 초기화
        - 공중에 있으면 중력이 점점 증가 (중력 가속)
        - 머리를 박으면 중력 즉시 0으로 리셋
        """
        if self.collisions["down"]:
            self.current_gravity = DEFAULT_GRAVITY
        else:
            self.current_gravity = min(
                MAX_GRAVITY * self.app.dt * 100,
                self.current_gravity + GRAVITY_STRENGTH * self.app.dt * 100
            )

        if self.collisions["up"]:
            self.current_gravity = 0

    def physics_movement(self):
        """
        movement 계산
        
        - 현재 속도 + 중력을 movement에 합산
        - velocity는 감쇠 (부드러운 정지 효과)
        """
        self.movement = pg.Vector2(self.velocity.x, self.velocity.y + self.current_gravity)

        # velocity 감쇠 (lerp 방식)
        self.velocity = self.velocity.lerp(pg.Vector2(0, 0), max(min(self.app.dt * VELOCITY_DRAG, 1), 0))

    def update(self):
        """
        매 프레임 호출
        
        - movement 계산
        - 충돌 검사 및 이동 적용
        - 중력 업데이트
        - 부모 업데이트 호출 (애니메이션 등)
        """
        self.physics_movement()
        self.physics_collision()
        self.physics_gravity()
        super().update()
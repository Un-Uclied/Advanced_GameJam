# collider_shapes.py
import pygame as pg
import math

class ColliderShape:
    def get_aabb(self, position: pg.Vector2) -> pg.Rect:
        """
        이 Shape의 AABB(Axis-Aligned Bounding Box)를 월드 좌표로 반환합니다.
        - position: Shape가 부착된 GameObject의 월드 포지션
        """
        raise NotImplementedError("Subclasses must implement get_aabb method.")

    def collide_with_shape(self, own_position: pg.Vector2, other_shape: 'ColliderShape', other_position: pg.Vector2) -> bool:
        """
        다른 ColliderShape과 충돌하는지 여부를 검사합니다.
        - own_position: 이 Shape의 GameObject 월드 포지션
        - other_shape: 다른 ColliderShape 인스턴스
        - other_position: 다른 Shape의 GameObject 월드 포지션
        """
        raise NotImplementedError("Subclasses must implement collide_with_shape method.")

class BoxShape(ColliderShape):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def get_aabb(self, position: pg.Vector2) -> pg.Rect:
        return pg.Rect(position.x - self.width / 2, position.y - self.height / 2, self.width, self.height)

    def collide_with_shape(self, own_position: pg.Vector2, other_shape: ColliderShape, other_position: pg.Vector2) -> bool:
        # Box-Box 충돌
        if isinstance(other_shape, BoxShape):
            rect1 = self.get_aabb(own_position)
            rect2 = other_shape.get_aabb(other_position)
            return rect1.colliderect(rect2)
        # Box-Circle 충돌
        elif isinstance(other_shape, CircleShape):
            # 원-박스 충돌 검사는 보통 원형이 박스 충돌 검사 로직을 호출하게 위임합니다.
            return other_shape.collide_with_shape(other_position, self, own_position)
        return False

class CircleShape(ColliderShape):
    def __init__(self, radius: float):
        self.radius = radius

    def get_aabb(self, position: pg.Vector2) -> pg.Rect:
        return pg.Rect(position.x - self.radius, position.y - self.radius, self.radius * 2, self.radius * 2)

    def collide_with_shape(self, own_position: pg.Vector2, other_shape: ColliderShape, other_position: pg.Vector2) -> bool:
        # Circle-Circle 충돌
        if isinstance(other_shape, CircleShape):
            dist_sq = (own_position.x - other_position.x)**2 + (own_position.y - other_position.y)**2
            radii_sum = self.radius + other_shape.radius
            return dist_sq < radii_sum**2
        # Circle-Box 충돌 (원의 중심에서 박스의 가장 가까운 점까지의 거리 이용)
        elif isinstance(other_shape, BoxShape):
            box_rect = other_shape.get_aabb(other_position)
            closest_x = max(box_rect.left, min(own_position.x, box_rect.right))
            closest_y = max(box_rect.top, min(own_position.y, box_rect.bottom))
            
            distance_sq = (own_position.x - closest_x)**2 + (own_position.y - closest_y)**2
            return distance_sq < self.radius**2
        return False
    

# physics_engine.py
import pygame as pg
from application import Time
from .components import Collider, RigidBody


class PhysicsEngine:
    _instance = None # 싱글턴 패턴

    def __init__(self):
        if PhysicsEngine._instance is not None:
            raise Exception("PhysicsEngine is a singleton!")
        PhysicsEngine._instance = self
        
        self.gravity = pg.Vector2(0, 9.81) # 기본 중력 (사이드뷰용)
        # self.gravity = pg.Vector2(0, 0) # 탑뷰에서는 중력을 0으로 설정 가능

    @classmethod
    def get_instance(cls):
        """PhysicsEngine의 싱글턴 인스턴스를 반환합니다."""
        if cls._instance is None:
            cls._instance = PhysicsEngine()
        return cls._instance

    def set_gravity(self, gravity_vector: pg.Vector2):
        """
        씬의 중력 값을 설정하고 모든 RigidBody에 적용합니다.
        - gravity_vector: 새로운 중력 벡터
        """
        self.gravity = gravity_vector
        for rb in RigidBody._all_rigid_bodies:
            rb.set_gravity(gravity_vector)

    def update(self):
        """매 프레임 물리 시뮬레이션을 업데이트합니다."""
        # 1. 모든 RigidBody의 속도 및 예상 위치 업데이트 (각 RigidBody.update에서 처리)
        # 이 단계는 RigidBody 컴포넌트의 update 메서드에서 이미 수행됩니다.

        # 2. 충돌 감지 (Broad Phase: AABB 검사)
        # 물리 반응이 필요한 콜라이더들 (is_trigger가 아닌)
        colliders_for_physics = [c for c in Collider._all_colliders if c.game_object and not c.is_trigger] 
        # 트리거 이벤트만 발생시키는 콜라이더들
        trigger_colliders = [c for c in Collider._all_colliders if c.game_object and c.is_trigger] 

        potential_collisions = [] # AABB를 통과한 잠재적 충돌 쌍

        # Non-trigger와 Non-trigger 콜라이더 간의 AABB 검사
        for i in range(len(colliders_for_physics)):
            for j in range(i + 1, len(colliders_for_physics)):
                col1 = colliders_for_physics[i]
                col2 = colliders_for_physics[j]
                
                rect1 = col1.get_world_aabb()
                rect2 = col2.get_world_aabb()

                if rect1.colliderect(rect2):
                    potential_collisions.append((col1, col2))
        
        # Non-trigger와 Trigger 콜라이더 간의 AABB 검사 (트리거 이벤트 발생용)
        for i in range(len(colliders_for_physics)):
            for j in range(len(trigger_colliders)):
                col1 = colliders_for_physics[i]
                col2 = trigger_colliders[j]

                rect1 = col1.get_world_aabb()
                rect2 = col2.get_world_aabb()

                if rect1.colliderect(rect2):
                    # 트리거 이벤트 발생 (예: col1.game_object.on_trigger_enter(col2.game_object))
                    pass 

        # 3. 충돌 해결 (Narrow Phase: 실제 Shape 기반 충돌 검사 및 반응)
        for col1, col2 in potential_collisions:
            # ColliderShape.collide_with_shape 메서드를 사용하여 정확한 충돌 검사
            if col1.shape.collide_with_shape(col1.game_object.position, col2.shape, col2.game_object.position):
                # 실제 충돌 발생 시 물리 반응 처리
                self._resolve_collision(col1, col2)

    def _resolve_collision(self, col1: Collider, col2: Collider):
        """
        두 콜라이더 간의 충돌을 해결하여 오브젝트 위치를 조정합니다.
        현재는 간단한 AABB 기반 분리만 구현되어 있습니다.
        - col1, col2: 충돌한 두 Collider 인스턴스
        """
        rb1 = col1.rigid_body
        rb2 = col2.rigid_body

        # 둘 중 하나라도 RigidBody가 없거나, 둘 다 키네마틱이면 물리 반응 없음
        if not rb1 and not rb2: return
        if rb1 and rb1.is_kinematic and rb2 and rb2.is_kinematic: return
        
        # 충돌 해제 로직 (RectShape만 고려한 간략화된 예시)
        # 실제로는 충돌한 Shape 타입에 따라 복잡한 알고리즘이 필요합니다.
        
        rect1 = col1.get_world_aabb()
        rect2 = col2.get_world_aabb()

        dx = rect2.centerx - rect1.centerx
        dy = rect2.centery - rect1.centery

        overlap_x = (rect1.width + rect2.width) / 2 - abs(dx)
        overlap_y = (rect1.height + rect2.height) / 2 - abs(dy)

        if overlap_x <= 0 or overlap_y <= 0: # 겹침이 없으면 처리 안함 (부동소수점 오차 때문)
            return

        move_vector = pg.Vector2(0, 0)
        
        if overlap_x < overlap_y: # X축 겹침이 더 적으면 X축으로 분리
            if dx > 0: move_vector.x = -overlap_x
            else: move_vector.x = overlap_x
        else: # Y축 겹침이 더 적으면 Y축으로 분리
            if dy > 0: move_vector.y = -overlap_y
            else: move_vector.y = overlap_y
        
        # 질량에 따른 이동량 분배 (한쪽이 키네마틱이면 해당 오브젝트만 이동)
        if rb1 and not rb1.is_kinematic and rb2 and not rb2.is_kinematic:
            total_mass = rb1.mass + rb2.mass
            if total_mass == 0: return # 질량이 둘 다 0인 경우 예외 처리

            # 질량 비율에 따라 이동량 분배
            rb1.game_object.position += move_vector * (rb2.mass / total_mass)
            rb2.game_object.position -= move_vector * (rb1.mass / total_mass)
        elif rb1 and not rb1.is_kinematic: # rb1만 움직일 수 있는 경우
            rb1.game_object.position += move_vector
        elif rb2 and not rb2.is_kinematic: # rb2만 움직일 수 있는 경우
            rb2.game_object.position -= move_vector

        # 충돌 후 속도 재조정 (탄성, 마찰 등)은 더 복잡한 물리 계산이 필요합니다.
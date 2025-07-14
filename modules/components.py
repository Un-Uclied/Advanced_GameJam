import pygame as pg
from .constants import *

class Component:
    '''모든 컴포넌트의 베이스 클래스'''
    def __init__(self):
        from .objects import GameObject
        self.game_object : GameObject | None = None  # 컴포넌트를 가진 오브젝트

    def on_start(self):
        '''오브젝트에 붙을 때 1회 호출'''
        pass

    def on_destroy(self):
        '''오브젝트에서 제거될 때 호출'''
        pass

    def update(self):
        '''매 프레임 업데이트'''
        pass

    def draw(self):
        '''매 프레임 그리기'''
        pass

class SpriteRenderer(Component):
    def __init__(self, image: pg.Surface, anchor: pg.Vector2 = pg.Vector2(0.5, 0.5), mask_color : pg.Color = pg.Color(0, 0, 0, 0)):
        super().__init__()
        self._original_image = image # 원본 이미지를 저장하여 매번 스케일링/회전 시 화질 저하 방지
        self.image = image
        self.anchor = anchor
        self.mask_color = mask_color

        '''캐싱 하는 이유가 매 프레임마다 rotate()나 scale() 부르면 성능 나락갈수도 있어서 그럼'''
        self._last_rotation = None # 이전 회전값을 캐싱하여 불필요한 연산 방지
        self._last_scale_factor = None # 이전 스케일값을 캐싱하여 불필요한 연산 방지
        self._last_gameobject_scale = None # GameObject의 이전 스케일값을 캐싱

        # 마스크 색상 적용 (최초 한 번만 적용)
        if self.mask_color.a != 0: # 알파값이 0이 아니면 마스크 색상으로 간주
            self._original_image.set_colorkey(self.mask_color)
            self.image.set_colorkey(self.mask_color) # 현재 image에도 적용

    def draw(self):
        #순환 참조 무서웡..
        from .camera import Camera2D
        from .application import Application

        game_object = self.game_object

        # 오브젝트의 월드 포지션
        pos = game_object.position

        # 총 스케일 계산: 카메라 스케일 * 오브젝트 스케일
        total_scale_x = Camera2D.scale * game_object.scale.x
        total_scale_y = Camera2D.scale * game_object.scale.y
        current_scale_factor = (total_scale_x, total_scale_y)

        # 이미지 변환 (회전, 스케일링) 최적화!!
        # 회전, 스케일, GameObject 스케일 중 하나라도 바뀌면 이미지 합성
        if (game_object.rotation != self._last_rotation or
            current_scale_factor != self._last_scale_factor or
            game_object.scale != self._last_gameobject_scale):
            

            scaled_by_object_and_camera_x = int(self._original_image.get_width() * total_scale_x)
            scaled_by_object_and_camera_y = int(self._original_image.get_height() * total_scale_y)

            # 스케일링된 이미지
            if scaled_by_object_and_camera_x > 0 and scaled_by_object_and_camera_y > 0:
                self.image = pg.transform.scale(
                    self._original_image, 
                    (scaled_by_object_and_camera_x, scaled_by_object_and_camera_y)
                )
            else: # 스케일이 0이거나 음수일 경우 렌더링 안함
                return 

            # 스케일링된 이미지를 회전
            self.image = pg.transform.rotate(self.image, game_object.rotation)

            # 캐시 업데이트
            self._last_rotation = game_object.rotation
            self._last_scale_factor = current_scale_factor
            self._last_gameobject_scale = game_object.scale

        # 이미지 크기 가져오기 (변환된 이미지의 크기)
        img_size = pg.Vector2(self.image.get_size())

        # 그리기 위치 계산 (월드 -> 스크린 -> 앵커 적용)
        draw_pos_screen = Camera2D.world_to_screen(pos)
        final_draw_pos = draw_pos_screen - img_size.elementwise() * self.anchor

        # 화면에 그리기
        Application.singleton.screen.blit(self.image, final_draw_pos)

from .physics import *

class RigidBody(Component):
    # 모든 RigidBody는 PhysicsEngine에 의해 관리될 예정입니다.
    # 이 리스트는 임시로 유지합니다.
    _all_rigid_bodies = [] 
    
    def __init__(self, mass: float = 1.0, gravity_scale: float = 1.0, is_kinematic: bool = False):
        super().__init__()
        self.mass = mass            # 질량
        self.gravity_scale = gravity_scale # 중력의 영향 정도
        self.is_kinematic = is_kinematic # 물리 계산에서 제외되고 수동으로 움직이는지 여부
        
        self.velocity = pg.Vector2(0, 0)     # 현재 속도
        self.acceleration = pg.Vector2(0, 0) # 현재 가속도

        self.collider: Collider = None # 이 RigidBody에 연결된 Collider 참조

        self._current_gravity = pg.Vector2(0, 0) # PhysicsEngine에서 설정될 현재 씬의 중력 벡터

    def on_start(self):
        # 같은 게임 오브젝트의 Collider 컴포넌트를 찾아 연결
        self.collider = self.game_object.get_component("Collider")
        if self.collider:
            self.collider.rigid_body = self

        RigidBody._all_rigid_bodies.append(self) # PhysicsEngine이 관리하도록 변경 예정

    def on_destroy(self):
        if self in RigidBody._all_rigid_bodies:
            RigidBody._all_rigid_bodies.remove(self)

    def update(self):
        from .application import Time
        # 키네마틱 오브젝트는 물리 영향을 받지 않습니다.
        if self.is_kinematic:
            return 

        # 가속도에 중력 적용
        self.acceleration += self._current_gravity * self.gravity_scale 

        # 속도 업데이트 (오일러 통합)
        # Application.get_delta_time()은 게임의 프레임 간 시간 간격을 제공해야 합니다.
        self.velocity += self.acceleration * Time.delta_time 

        # 위치 업데이트
        # 이 위치 업데이트는 PhysicsEngine의 충돌 해결 전에 임시로 적용될 수 있습니다.
        # 최종 위치는 PhysicsEngine에서 조정될 수 있습니다.
        self.game_object.position += self.velocity * Time.delta_time

        # 가속도 초기화 (매 프레임 외부 힘이 작용하지 않으면 0)
        self.acceleration = pg.Vector2(0, 0)

    def apply_force(self, force: pg.Vector2):
        """
        이 RigidBody에 힘을 가합니다 (F=ma => a=F/m).
        - force: 가할 힘 벡터
        """
        if self.mass > 0:
            self.acceleration += force / self.mass

    def set_gravity(self, gravity_vector: pg.Vector2):
        """
        이 RigidBody에 적용될 중력 값을 설정합니다.
        PhysicsEngine에서 호출됩니다.
        - gravity_vector: 중력 벡터
        """
        self._current_gravity = gravity_vector

class Collider(Component):
    # 모든 콜라이더는 PhysicsEngine에 의해 관리될 예정입니다.
    # 이 리스트는 임시로 유지합니다.
    _all_colliders = [] 

    def __init__(self, shape: ColliderShape, is_trigger: bool = False):
        super().__init__()
        self.shape = shape
        self.is_trigger = is_trigger # 물리 반응 없이 이벤트만 발생
        self.rigid_body = None       # 이 콜라이더와 연결된 RigidBody 참조

    def on_start(self):
        # 같은 게임 오브젝트의 RigidBody 컴포넌트를 찾아 연결
        # RigidBody 클래스가 정의된 후에 사용 가능합니다.
        self.rigid_body = self.game_object.get_component(RigidBody) 
    
        if self.rigid_body:
            self.rigid_body.collider = self

        Collider._all_colliders.append(self) # PhysicsEngine이 콜라이더를 관리하도록 변경 예정

    def on_destroy(self):
        if self in Collider._all_colliders:
            Collider._all_colliders.remove(self)

    def get_world_aabb(self) -> pg.Rect:
        """이 콜라이더의 월드 좌표계 AABB를 반환합니다 (충돌 광역 검사용)."""
        return self.shape.get_aabb(self.game_object.position)


# =======================================
# 🧪 ObjectDebugger: 디버그용 도구
# =======================================

class ObjectDebugger(Component):
    def __init__(self):
        super().__init__()

    def draw(self):
        if not self.object:
            return

        from .camera import Camera2D
        from .application import Application
        screen = Application.singleton.screen
        pos = self.object.position

        # 위쪽 방향 (빨간 선)
        pg.draw.line(screen, pg.Color(255, 0, 0), 
                     Camera2D.world_to_screen(pos),
                     Camera2D.world_to_screen(pos + self.object.up * 500), 20)

        # 오른쪽 방향 (초록 선)
        pg.draw.line(screen, pg.Color(0, 255, 0),
                     Camera2D.world_to_screen(pos),
                     Camera2D.world_to_screen(pos + self.object.right * 500), 20)

        # 콜라이더 시각화 (파란 사각형)
        collider = self.object.get_component(Collider)
        if collider:
            rect = collider.get_rect()
            pg.draw.rect(screen, pg.Color(0, 0, 255),
                         (Camera2D.world_to_screen(rect.topleft),
                          pg.Vector2(rect.size) * Camera2D.scale), 2)

        # 중심점 (노란 점)
        pg.draw.circle(screen, pg.Color(255, 255, 0),
                       Camera2D.world_to_screen(pos), 10)


# =======================================
# 🔤 TextRenderer: 텍스트 표시
# =======================================

class TextRenderer(Component):
    def __init__(self, text: str, font_size: int = 24,
                 color: pg.Color = pg.Color(255, 255, 255),
                 font_name="Galmuri11.ttf"):
        super().__init__()
        self.text = text
        self.font_size = font_size
        self.color = color
        self.font = pg.freetype.Font(DEFAULT_FONT_PATH + font_name, font_size)

    def draw(self):
        if not self.object:
            return

        from .camera import Camera2D
        from .application import Application
        pos = Camera2D.world_to_screen(self.object.position)
        self.font.render_to(Application.singleton.screen, pos, self.text, self.color)
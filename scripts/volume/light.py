import pygame as pg

from scripts.constants import *
from scripts.camera import *
from scripts.utils import *

class Light(GameObject):
    """
    고정 크기와 강도의 원형 빛 효과 객체.

    빛의 모양, 위치, 밝기 등을 설정할 수 있으며, 씬의 `draw_lights` 메서드를
    통해 한번에 렌더링됨.

    Attributes:
        position (pg.Vector2): 빛의 중심 위치 (월드 좌표).
        size (float): 빛의 반경을 결정하는 크기.
        strength (float): 빛의 최대 알파값 (투명도, 0-255).
        fade_out (float): 빛이 희미해지는 간격.
        segments (int): 빛의 그라데이션을 표현하기 위해 겹쳐 그릴 원의 개수.
        surface (pg.Surface): 미리 렌더링된 빛 효과 이미지.
    """

    def __init__(self,
                 size: float,
                 position: pg.Vector2,
                 strength: float = 25,
                 fade_out: float = 10,
                 segments: int = 15):
        """
        Light 객체를 초기화함.

        Args:
            size (float): 빛의 반경을 결정하는 Surface 크기 (픽셀 단위, 정사각형).
            position (pg.Vector2): 빛 중심 위치 (월드 좌표).
            strength (float): 빛의 최대 알파값 (투명도, 0~255).
            fade_out (float): 빛의 그라데이션 간격.
            segments (int): 빛의 그라데이션을 위해 겹쳐 그릴 원의 개수.
        """
        # 부모 클래스인 GameObject의 생성자를 호출해서 씬에 등록함.
        super().__init__()

        self.position = position
        self.size = size
        self.strength = strength
        self.fade_out = fade_out
        self.segments = segments
        
        # 성능 최적화를 위해 빛의 Surface를 생성 시 한 번만 그림.
        self.surface = self.create_light_surface()

    def create_light_surface(self) -> pg.Surface:
        """
        빛의 그라데이션 효과를 가진 Surface를 생성하고 반환함.
        """
        # 반투명 효과를 위해 SRCALPHA 플래그를 사용해 Surface를 생성함.
        surface = pg.Surface((self.size, self.size), pg.SRCALPHA)
        
        # 여러 개의 원을 겹쳐서 부드러운 빛 그라데이션을 만듦.
        for i in range(self.segments):
            # 각 원의 알파값을 계산. i가 커질수록 알파값이 증가함.
            alpha = min(i * self.strength, 255)
            # 현재 원의 반지름을 계산. i가 커질수록 반지름이 작아짐.
            radius = self.size / 2 - i * self.fade_out
            
            # 반지름이 양수일 때만 원을 그림.
            if radius > 0:
                pg.draw.circle(
                    surface,
                    (255, 255, 255, alpha),  # 흰색에 계산된 알파값 적용.
                    (self.size / 2, self.size / 2),  # Surface의 중앙에 그림.
                    radius
                )
        return surface

    @property
    def bound_box(self) -> pg.Rect:
        """빛의 월드 좌표계 내 경계 사각형 (중심 위치 기준)을 반환함."""
        # 0,0에서 시작하는 사각형을 생성하고 중심을 현재 위치로 설정함.
        rect = pg.Rect(0, 0, self.size, self.size)
        rect.center = self.position
        return rect

class LightManager:
    """
    씬에 존재하는 모든 빛 객체를 관리하고 렌더링하는 클래스.
    
    """
    def __init__(self, scene):
        """
        LightManager를 초기화함.
        
        Args:
            scene (Scene): LightManager가 속한 씬 객체.
        """
        self.scene = scene

    def draw_lights(self, surface: pg.Surface):
        """
        씬에 존재하는 모든 Light 객체를 받아서 surface에 빛 효과를 적용함.
        
        `BLEND_RGBA_SUB` 모드를 사용해서 빛이 있는 부분의 색을 빼, 구멍 뚫린 효과를 연출함.
        
        Args:
            surface (pg.Surface): 빛 효과를 적용할 대상 Surface.
        """
        # 씬에 등록된 모든 Light 객체를 가져옴.
        all_lights = self.scene.get_objects_by_types(Light)
        
        # 각 빛 객체를 순회하며 그림.
        for light in all_lights:
            # 카메라 뷰포트 밖의 빛은 그리지 않아서 성능을 최적화함.
            if not CameraView.is_rect_in_view(self.scene.camera, light.bound_box):
                continue

            # 월드 좌표계의 Rect -> 스크린 좌표계의 Rect
            screen_rect = CameraView.world_rect_to_screen_rect(self.scene.camera, light.bound_box)
            # BLEND_RGBA_SUB 모드로 빛 이미지를 그림.
            surface.blit(light.surface, screen_rect.topleft, special_flags=pg.BLEND_RGBA_SUB)

    def is_rect_in_light(self, rect: pg.Rect) -> bool:
        """
        주어진 사각형(월드 좌표계)이 씬에 존재하는 어떤 빛에라도 닿아있는지 판단함.
        
        Args:
            rect (pg.Rect): 충돌을 확인할 사각형.
            
        Returns:
            bool: 사각형이 빛 범위 내에 있으면 True, 아니면 False.
        """
        # 씬에 등록된 모든 Light 객체를 가져옴.
        all_lights = self.scene.get_objects_by_types(Light)
        
        # 각 빛 객체를 순회하며 충돌을 검사함.
        for light in all_lights:
            # 먼저 사각형과 빛의 경계 사각형이 충돌하는지 확인해서 불필요한 카메라 뷰포트 체크를 줄임.
            if light.bound_box.colliderect(rect):
                # 충돌이 감지되면 True를 바로 반환함.
                return True
        return False
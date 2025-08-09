import pygame as pg

from scripts.constants import *
from scripts.camera import *
from scripts.core import *

LIGHT_SEGMENTS = 15   # 원형 빛을 겹쳐 그릴 횟수 (겹침 많을수록 부드러움↑)
LIGHT_FADE_OUT = 10   # 각 원이 작아지는 간격 (빛의 점점 희미해짐 효과)

class Light(GameObject):
    """
    고정 크기와 강도의 원형 빛 효과 객체.

    특징:
    - size, strength는 생성 시에만 설정 가능 (런타임에 변경 불가)
    - 위치는 언제든지 변경 가능 (position 프로퍼티)
    - 성능 최적화를 위해 빛 Surface를 한 번만 생성함
    - 여러 개 생성해도 draw_lights() 호출로 한번에 처리 가능

    :param size: 빛 반경을 결정하는 Surface 크기 (픽셀 단위, 정사각형)
    :param position: 빛 중심 위치 (월드 좌표)
    :param strength: 빛의 최대 알파값 (투명도, 0~255)
    """

    def __init__(self, size: float, position: pg.Vector2, strength: float = 25):
        super().__init__()

        self.position = position

        # 빛 Surface 생성 (반투명)
        self.surface = pg.Surface((size, size), pg.SRCALPHA)

        # 여러 개의 원을 겹쳐서 부드러운 빛 그라데이션 생성
        for i in range(LIGHT_SEGMENTS):
            alpha = min(i * strength, 255)
            pg.draw.circle(
                self.surface,
                (255, 255, 255, alpha),           # 흰색, 알파값 점점 증가
                (size / 2, size / 2),             # Surface 중앙
                size / 2 - i * LIGHT_FADE_OUT     # 반지름 점점 작아짐
            )

    @property
    def bound_box(self) -> pg.Rect:
        """빛의 월드 좌표계 내 경계 사각형 (중앙 위치 기준)"""
        rect = pg.Rect(self.position, self.surface.get_size())
        rect.center = self.position
        return rect

    @classmethod
    def draw_lights(cls, camera: Camera2D, surface: pg.Surface):
        """
        현재 씬에 존재하는 모든 Light 객체를 받아서
        전달된 surface에 BLEND_RGBA_SUB 모드로 빛 효과를 적용.

        BLEND_RGBA_SUB는 surface의 색상값에서 빛 색상만큼 뺌 → 구멍 뚫린 듯한 효과 연출.
        """
        all_lights = GameObject.get_objects_by_types(cls)
        for light in all_lights:
            # 카메라 뷰 밖에 있으면 성능 위해 그리지 않음
            if not CameraView.is_in_view(camera, light.bound_box):
                continue

            screen_rect = CameraView.world_rect_to_screen(camera, light.bound_box)
            surface.blit(light.surface, screen_rect.topleft, special_flags=pg.BLEND_RGBA_SUB)

    @classmethod
    def is_rect_in_light(cls, camera: Camera2D, rect: pg.Rect) -> bool:
        """
        주어진 rect(월드 좌표계)가 현재 씬의 어떤 빛에라도 닿아있는지 여부 판단.

        빛 범위 내 있으면 True, 없으면 False 반환.
        """
        all_lights = GameObject.get_objects_by_types(cls)
        for light in all_lights:
            if not CameraView.is_in_view(camera, light.bound_box):
                continue
            if light.bound_box.colliderect(rect):
                return True
        return False
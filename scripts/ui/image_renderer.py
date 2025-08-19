import pygame as pg

from scripts.constants import *
from scripts.camera import *
from scripts.utils import *

class ImageRenderer(GameObject):
    """
    UI용 이미지 렌더러 (포지션, 스케일, 앵커 지원 + Tween 가능)

    Args:
        image (pg.Surface): 렌더할 이미지 (절대 에셋 키 아님, 직접 Surface 전달)
        position (pg.Vector2): 렌더 위치 (스크린 좌표)
        scale (float): 이미지 스케일 (기본 1.0)
        anchor (pg.Vector2): 앵커 기준 (0~1, 기본 중앙 0.5,0.5)
        use_camera (bool): 월드 좌표 기준 렌더링 여부 (기본 False)
    """
    def __init__(self, 
                 image: pg.Surface, 
                 position: pg.Vector2, 
                 scale: float = 1.0, 
                 anchor: pg.Vector2 = pg.Vector2(0.5, 0.5), 
                 use_camera: bool = False):
        super().__init__()
        self.image = image
        self.scale = scale
        self.pos = position
        self.anchor = anchor
        self.use_camera = use_camera

    @property
    def size(self) -> pg.Vector2:
        """스케일 적용된 이미지 크기 반환"""
        return pg.Vector2(self.image.get_size()) * self.scale

    @property
    def screen_pos(self) -> pg.Vector2:
        """앵커 기준 실제 렌더링 위치 계산"""
        return self.pos - self.size.elementwise() * self.anchor

    @property
    def rect(self) -> pg.Rect:
        """마우스 충돌 판정용 사각형"""
        return pg.Rect(self.screen_pos, self.size)

    def draw(self):
        super().draw()

        surface = self.app.surfaces[LAYER_INTERFACE]

        # 스케일 적용 이미지 생성 (스무스 스케일 아님, 필요 시 바꿔도 됨)
        scaled_img = pg.transform.scale_by(self.image, self.scale)

        draw_pos = self.screen_pos
        if self.use_camera:
            draw_pos = CameraMath.world_to_screen(self.scene.camera, draw_pos)

        surface.blit(scaled_img, draw_pos)
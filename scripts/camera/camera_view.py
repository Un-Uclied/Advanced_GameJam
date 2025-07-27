import pygame as pg

from scripts.constants import *

from .camera_math import CameraMath
from .camera import Camera2D

WHOLE_SCREEN_RECT = pg.Rect((0, 0), SCREEN_SIZE)

class CameraView:
    @staticmethod
    def get_scaled_surface(camera: Camera2D, surface: pg.Surface) -> pg.Surface:
        '''카메라 줌에 맞게 이미지 크기 조절 | scale이 1이면 최적화를 위해 원본 반환'''
        return surface if camera.scale == 1 else pg.transform.scale_by(surface, camera.scale)

    @staticmethod
    def world_rect_to_screen(camera: Camera2D, rect: pg.Rect) -> pg.Rect:
        '''월드 rect를 스크린 rect로 변환'''
        screen_pos = CameraMath.world_to_screen(camera, pg.Vector2(rect.topleft))
        screen_size = pg.Vector2(rect.size) * camera.scale
        return pg.Rect(screen_pos, screen_size)

    @staticmethod
    def is_in_view(camera: Camera2D, rect: pg.Rect) -> bool:
        '''카메라를 받고, 월드 rect를 받으후 스크린 rect로 변환후 계산'''
        screen_rect = CameraView.world_rect_to_screen(camera, rect)
        return WHOLE_SCREEN_RECT.colliderect(screen_rect)
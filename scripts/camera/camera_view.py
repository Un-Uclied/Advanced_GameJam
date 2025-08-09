import pygame as pg

from scripts.constants import *
from .camera_math import CameraMath
from .camera import Camera2D

WHOLE_SCREEN_RECT = pg.Rect((0, 0), SCREEN_SIZE)  # 스크린 전체 영역 Rect

def is_rects_intersect(rect1: pg.Rect, rect2: pg.Rect) -> bool:
    '''
    AABB 충돌 검사
    두 Rect가 겹치는지 빠르게 체크함 (pygame.Rect.colliderect와 비슷함)

    :param rect1: 첫 번째 Rect
    :param rect2: 두 번째 Rect
    :return: 겹치면 True, 아니면 False
    '''
    return not (rect1.right < rect2.left or
                rect1.left > rect2.right or
                rect1.bottom < rect2.top or
                rect1.top > rect2.bottom)

class CameraView:
    @staticmethod
    def world_rect_to_screen(camera: Camera2D, rect: pg.Rect) -> pg.Rect:
        '''
        월드 좌표계에 있는 Rect를 스크린 좌표계 Rect로 변환

        :param camera: 현재 카메라 객체
        :param rect: 월드 좌표 기준 Rect
        :return: 스크린 좌표 기준 Rect
        '''
        screen_pos = CameraMath.world_to_screen(camera, pg.Vector2(rect.topleft))
        screen_size = pg.Vector2(rect.size)
        return pg.Rect(screen_pos, screen_size)

    @staticmethod
    def is_in_view(camera: Camera2D, rect: pg.Rect) -> bool:
        '''
        주어진 월드 Rect가 카메라 뷰포트(화면)에 보이는지 체크

        :param camera: 현재 카메라 객체 (보통 self.app.scene.camera)
        :param rect: 월드 좌표 기준 Rect (절대 좌표)
        :return: 화면에 보이면 True, 아니면 False
        '''
        screen_rect = CameraView.world_rect_to_screen(camera, rect)
        return is_rects_intersect(WHOLE_SCREEN_RECT, screen_rect)

    @staticmethod
    def get_view_rect(camera: Camera2D) -> pg.Rect:
        '''
        카메라 중심 위치를 기준으로 화면 크기 만큼의 Rect 반환

        :param camera: 현재 카메라 객체
        :return: 월드 좌표 기준 카메라가 보는 화면 영역 Rect
        '''
        # 카메라 위치는 화면 좌상단 기준이 아니므로 주의 필요
        return pg.Rect(camera.position, SCREEN_SIZE)
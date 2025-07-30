import pygame as pg

from scripts.constants import *

from .camera_math import CameraMath
from .camera import Camera2D

WHOLE_SCREEN_RECT = pg.Rect((0, 0), SCREEN_SIZE)

class CameraView:
    @staticmethod
    def world_rect_to_screen(camera: Camera2D, rect: pg.Rect) -> pg.Rect:
        '''월드 rect를 스크린 rect로 변환'''
        screen_pos = CameraMath.world_to_screen(camera, pg.Vector2(rect.topleft))
        screen_size = pg.Vector2(rect.size)
        return pg.Rect(screen_pos, screen_size)

    @staticmethod
    def is_in_view(camera: Camera2D, rect: pg.Rect) -> bool:
        '''
        카메라를 받고, 월드 rect를 받으후 스크린 rect로 변환후 계산
        
        :param camera: 걍 현재 카메라 ㅇㅇ; 게임 오브젝트에선 self.app.scene.camera로 접근 가능
        :param rect: 절대 월드 좌표계 Rect면 안된다 !!!
        '''

        screen_rect = CameraView.world_rect_to_screen(camera, rect)
        return WHOLE_SCREEN_RECT.colliderect(screen_rect)
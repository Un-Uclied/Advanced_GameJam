import pygame as pg

from scripts.constants import *

from .camera import Camera2D

class CameraMath:
    @staticmethod
    def world_to_screen(camera: Camera2D, world_pos: pg.Vector2) -> pg.Vector2:
        '''월드 좌표계에서 스크린 좌표계로 ㄱㄱ (예: 카메라에 영향 받는 모든 오브젝트나 엔티티는 무조건 이걸 거치고 렌더해야함!!)'''
        anchor_pixel = SCREEN_SIZE.elementwise() * camera.anchor
        return anchor_pixel + (world_pos - (camera.position + camera.shake_offset))

    @staticmethod
    def screen_to_world(camera: Camera2D, screen_pos: pg.Vector2) -> pg.Vector2:
        '''스크린 좌표계에서 월드 좌표계로 ㄱㄱ (예: 마우스위치를 월드 위치로 변경 가능)'''
        anchor_pixel = SCREEN_SIZE.elementwise() * camera.anchor
        return (screen_pos - anchor_pixel) + (camera.position + camera.shake_offset)
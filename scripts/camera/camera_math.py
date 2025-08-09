import pygame as pg

from scripts.constants import *
from .camera import Camera2D

class CameraMath:
    @staticmethod
    def world_to_screen(camera: Camera2D, world_pos: pg.Vector2) -> pg.Vector2:
        '''
        월드 좌표를 스크린 좌표로 변환

        - 카메라 위치와 흔들림(shake_offset)을 반영해서 계산
        - 화면 크기와 카메라 앵커(anchor)를 기준으로 오프셋 적용
        - 모든 카메라 영향을 받는 오브젝트는 이 함수로 위치 변환 후 렌더해야 함

        :param camera: 현재 카메라 객체
        :param world_pos: 월드 좌표 (Vector2)
        :return: 스크린 좌표 (Vector2)
        '''
        anchor_pixel = SCREEN_SIZE.elementwise() * camera.anchor
        return anchor_pixel + (world_pos - (camera.position + camera.shake_offset))

    @staticmethod
    def screen_to_world(camera: Camera2D, screen_pos: pg.Vector2) -> pg.Vector2:
        '''
        스크린 좌표를 월드 좌표로 변환

        - 마우스 위치 등 스크린 좌표를 월드 공간 위치로 변환할 때 사용
        - 카메라 위치와 흔들림(shake_offset), 앵커 기준으로 보정함

        :param camera: 현재 카메라 객체
        :param screen_pos: 스크린 좌표 (Vector2)
        :return: 월드 좌표 (Vector2)
        '''
        anchor_pixel = SCREEN_SIZE.elementwise() * camera.anchor
        return (screen_pos - anchor_pixel) + (camera.position + camera.shake_offset)
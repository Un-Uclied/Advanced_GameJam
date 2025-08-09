import pygame as pg
import os

from scripts.constants import *

BASE_IMAGE_PATH = "assets/images/"

def load_image(path: str, scale: float = 1, tint_color: pg.Color = None) -> pg.Surface:
    '''
    단일 이미지 로드 + 스케일 조절 + 틴트 적용
    
    :param path: BASE_IMAGE_PATH 기준 상대 경로
    :param scale: 배율, 1이면 원본 크기
    :param tint_color: pg.Color or None, None이면 틴트 없음
    :return: 변환된 Surface
    '''
    full_path = BASE_IMAGE_PATH + path
    surface = pg.image.load(full_path).convert_alpha()

    if scale != 1:
        surface = pg.transform.scale_by(surface, scale)

    if tint_color is not None:
        apply_tint(surface, tint_color)

    return surface


def load_images(path: str, scale: float = 1, tint_color: pg.Color = None) -> list[pg.Surface]:
    '''
    폴더 내 모든 이미지 로드 후 정렬해서 리스트 반환
    
    :param path: BASE_IMAGE_PATH 기준 폴더 경로
    :param scale: 배율
    :param tint_color: 틴트 색상 or None
    :return: Surface 리스트
    '''
    dir_path = BASE_IMAGE_PATH + path
    filenames = sorted(os.listdir(dir_path))

    return [load_image(f"{path}/{filename}", scale, tint_color) for filename in filenames]


def apply_tint(image: pg.Surface, tint: pg.Color):
    '''
    이미지에 틴트 적용
    
    :param image: pg.Surface 대상 이미지 (원본 직접 변환)
    :param tint: pg.Color 틴트 색상
    '''
    overlay = pg.Surface(image.get_size(), pg.SRCALPHA)
    overlay.fill(tint)
    image.blit(overlay, (0, 0), special_flags=pg.BLEND_MULT)
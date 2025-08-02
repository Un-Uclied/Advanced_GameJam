import pygame as pg
import os

from scripts.constants import *

BASE_IMAGE_PATH = "assets/images/"

def load_image(path : str, scale : float = 1, tint_color : pg.Color = None) -> pg.Surface:
    '''한개의 이미지를 반환 | tint_color가 None이면 틴트 적용 안함. | 스케일도 적용 가능'''
    #convert_alpha()로 뒤에 배경 없게 알파값까지 챙기기
    surface = pg.image.load(BASE_IMAGE_PATH + path).convert_alpha()

    #스케일이 1이면 굳이 할필요 없음
    surface = surface if scale == 1 else pg.transform.scale_by(surface, scale)
    
    apply_tint(surface, tint_color)

    return surface

def load_images(path : str, scale : int = 1, tint_color : pg.Color = None) -> list[pg.Surface]:
    '''지정된 폴더 안에 있는 이미지들을 이름 순서대로 반환'''
    surfaces = []
    for img_name in sorted(os.listdir(BASE_IMAGE_PATH + path)):
        surfaces.append(load_image(path + '/' + img_name, scale, tint_color))
    return surfaces

def apply_tint(image : pg.Surface, tint : pg.Color):
    '''간단한 틴트 적용'''
    if tint is None: return 
    overlay = pg.Surface(image.get_size(), pg.SRCALPHA)
    overlay.fill(tint)
    image.blit(overlay, (0, 0), special_flags=pg.BLEND_MULT)
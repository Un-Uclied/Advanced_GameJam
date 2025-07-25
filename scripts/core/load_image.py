import pygame as pg
import os

from datas.const import *

def load_image(path : str, scale : int = 0, tint_color : pg.Color = "") -> pg.Surface:
    img = pg.image.load(BASE_IMAGE_PATH + path).convert_alpha()
    
    if scale == 0:
        img = pg.transform.scale_by(img, ASSET_SCALE_BY)
    elif not scale == 1:
        img = pg.transform.scale_by(img, scale)
    
    if not tint_color == "":
        apply_tint(img, tint_color)

    return img

def load_images(path : str, scale : int = 0, tint_color : pg.Color = "") -> list[pg.Surface]:
    images = []
    for img_name in sorted(os.listdir(BASE_IMAGE_PATH + path)):
        images.append(load_image(path + '/' + img_name, scale, tint_color))
    return images

def apply_tint(image : pg.Surface, tint : pg.Color):
    overlay = pg.Surface(image.get_size(), pg.SRCALPHA)
    overlay.fill(tint)
    image.blit(overlay, (0, 0), special_flags=pg.BLEND_MULT)
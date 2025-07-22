import pygame as pg
import os

from datas.const import *

def load_image(path : str, scale : int = 0) -> pg.Surface:
    img = pg.image.load(BASE_IMAGE_PATH + path).convert_alpha()
    if scale == 0:
        img = pg.transform.scale_by(img, ASSET_SCALE_BY)
    elif not scale == 1:
        img = pg.transform.scale_by(img, scale)
    return img

def load_images(path : str, scale : int = 0) -> list[pg.Surface]:
    images = []
    for img_name in sorted(os.listdir(BASE_IMAGE_PATH + path)):
        images.append(load_image(path + '/' + img_name, scale))
    return images
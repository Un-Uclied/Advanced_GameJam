import pygame as pg
import os

from datas.const import *

def load_image(path : str) -> pg.Surface:
    img = pg.image.load(BASE_IMAGE_PATH + path).convert()
    img.set_colorkey((0,0,0))
    return img

def load_images(path : str) -> list[pg.Surface]:
    images = []
    for img_name in sorted(os.listdir(BASE_IMAGE_PATH + path)):
        images.append(load_image(path + '/' + img_name))
    return images
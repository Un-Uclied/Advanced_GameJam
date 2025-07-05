#외부 라이브러리 임포트
import pygame as pg
import os

#내부 라이브러리 임포트
from .constants import DEFAULT_IMAGE_PATH

def load_image(image_path : str = "place_holder.jpg"):
    surface = pg.image.load(DEFAULT_IMAGE_PATH + image_path).convert_alpha()
    return surface

def load_images(path):
    images = []
    for img_name in sorted(os.listdir(DEFAULT_IMAGE_PATH + path)):
        images.append(load_image(path + '/' + img_name))
    return images
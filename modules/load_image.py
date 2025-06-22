import pygame as pg
import os

DEFAULT_SPRITE_PATH = "assets/sprites/"

def load_sprite(image_path : str = "place_holder.jpg"):
    surface = pg.image.load(DEFAULT_SPRITE_PATH + image_path).convert_alpha()
    return surface

def load_sprites(path):
    images = []
    for img_name in sorted(os.listdir(DEFAULT_SPRITE_PATH + path)):
        images.append(load_sprite(path + '/' + img_name))
    return images
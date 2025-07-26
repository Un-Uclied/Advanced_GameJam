import pygame as pg
import os

from scripts.constants.app_settings import *

BASE_IMAGE_PATH = "assets/images/"

def load_image(path : str, scale : float = 1, tint_color : pg.Color = "") -> pg.Surface:
    surface = pg.image.load(BASE_IMAGE_PATH + path).convert_alpha()
    surface = surface if scale == 1 else pg.transform.scale_by(surface, scale)
    
    if not tint_color == "":
        apply_tint(surface, tint_color)

    return surface

def load_images(path : str, scale : int = 1, tint_color : pg.Color = "") -> list[pg.Surface]:
    surfaces = []
    for img_name in sorted(os.listdir(BASE_IMAGE_PATH + path)):
        surfaces.append(load_image(path + '/' + img_name, scale, tint_color))
    return surfaces

def apply_tint(image : pg.Surface, tint : pg.Color):
    overlay = pg.Surface(image.get_size(), pg.SRCALPHA)
    overlay.fill(tint)
    image.blit(overlay, (0, 0), special_flags=pg.BLEND_MULT)
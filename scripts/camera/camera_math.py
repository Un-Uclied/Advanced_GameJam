import pygame as pg

from scripts.constants import *

from .camera import Camera2D

class CameraMath:
    @staticmethod
    def world_to_screen(camera: Camera2D, world_pos: pg.Vector2) -> pg.Vector2:
        anchor_pixel = SCREEN_SIZE.elementwise() * camera.anchor
        return anchor_pixel + (world_pos - (camera.position + camera.shake_offset)) * camera.scale

    @staticmethod
    def screen_to_world(camera: Camera2D, screen_pos: pg.Vector2) -> pg.Vector2:
        anchor_pixel = SCREEN_SIZE.elementwise() * camera.anchor
        return (screen_pos - anchor_pixel) / camera.scale + (camera.position + camera.shake_offset)
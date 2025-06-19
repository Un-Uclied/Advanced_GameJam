import pygame as pg

from singleton import singleton
from appplication import Application

@singleton
class RenderManager:
    def __init__(self):
        self.app = Application()

        self.layers = {
            "bg": pg.sprite.LayeredUpdates(),
            "default": pg.sprite.LayeredUpdates(),
            "ui": pg.sprite.LayeredUpdates()
        }
        self.layer_lookup = {}  # sprite → layer_name

    def add(self, sprite, layer_name="default"):
        self.layers[layer_name].add(sprite)
        self.layer_lookup[sprite] = layer_name

    def remove(self, sprite):
        layer = self.layer_lookup.get(sprite)
        if layer:
            self.layers[layer].remove(sprite)
            del self.layer_lookup[sprite]

    def draw_all(self, surface, camera):
        for layer_name in ["bg", "default"]:  # UI는 따로 그릴 수도 있음
            for sprite in self.layers[layer_name]:
                screen_pos = camera.apply(sprite.rect.topleft)
                surface.blit(sprite.image, screen_pos)
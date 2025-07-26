import pygame as pg
import random

from scripts.constants import *
from scripts.objects import GameObject

CLOUD_MIN_SPEED = .45
CLOUD_MAX_SPEED = 1.2

CLOUD_MIN_DEPTH = .2
CLOUD_MAX_DEPTH = .8

CLOUD_ALPHA = 65

class Cloud(GameObject):
    def __init__(self, pos: pg.Vector2, img: pg.Surface, speed: float, depth: float):
        super().__init__()
        self.pos = pg.Vector2(pos)
        self.img = img
        self.size = pg.Vector2(self.img.get_size())
        self.speed = speed
        self.depth = depth
        self.img.set_alpha(CLOUD_ALPHA)

    def on_update(self):
        super().on_update()
        self.pos.x += self.speed

    def on_draw(self):
        super().on_draw()
        surface = self.app.surfaces[LAYER_BG]
        camera = self.app.scene.camera

        depth_pos = self.pos - (camera.position * self.depth)

        clamped_x = depth_pos.x % (SCREEN_SIZE.x + self.size.x) - self.size.x
        clamped_y = depth_pos.y % (SCREEN_SIZE.y + self.size.y) - self.size.y

        screen_pos = pg.Vector2(clamped_x, clamped_y)
        surface.blit(self.img, screen_pos)

class Clouds(GameObject):
    def __init__(self, cloud_count: int = 16):
        super().__init__()
        cloud_surfaces = self.app.ASSETS["backgrounds"]["clouds"]
        self.clouds: list[Cloud] = []

        for _ in range(cloud_count):
            pos = pg.Vector2(random.random() * 99999, random.random() * 99999)
            img = random.choice(cloud_surfaces)
            speed = random.uniform(CLOUD_MIN_SPEED, CLOUD_MAX_SPEED)
            depth = random.uniform(CLOUD_MIN_DEPTH, CLOUD_MAX_DEPTH)
            self.clouds.append(Cloud(pos, img, speed, depth))

        self.clouds.sort(key=lambda cloud: cloud.depth)

    def on_update(self):
        super().on_update()
        for cloud in self.clouds:
            cloud.on_update()

    def on_draw(self):
        super().on_draw()
        for cloud in self.clouds:
            cloud.on_draw()
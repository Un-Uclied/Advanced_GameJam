import pygame as pg

from datas.const import *
from scripts.objects import GameObject

class Outline(GameObject):
    def __init__(self, entity, color, thickness = 1):
        super().__init__()
        self.enabled = True

        self.entity = entity
        self.color = color
        self.thickness = thickness

    def on_draw(self):
        if not self.enabled:
            return
        camera = self.entity.app.scene.camera
        screen = self.entity.app.surfaces[LAYER_ENTITY]
        entity = self.entity

        world_position = pg.Vector2(entity.rect.topleft) + entity.flip_offset[entity.flip_x]
        image = entity.anim.img()

        if not camera.is_in_view(pg.Rect(world_position, image.get_size())) : return

        image = camera.get_scaled_surface(image)

        mask = pg.mask.from_surface(image)
        outline_surface = mask.to_surface(setcolor=self.color, unsetcolor=(0, 0, 0, 0))
        outline_surface.set_colorkey((0, 0, 0))
        outline_surface = pg.transform.flip(outline_surface, entity.flip_x, False)

        position = camera.world_to_screen(world_position)

        for dx in range(-self.thickness, self.thickness + 1):
            for dy in range(-self.thickness, self.thickness + 1):
                if dx == 0 and dy == 0:
                    continue
                screen.blit(outline_surface, (position[0] + dx, position[1] + dy))
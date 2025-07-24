import pygame as pg

from datas.const import *
from .objects import *

class Outline(GameObject):
    def __init__(self, entity, color, thickness):
        super().__init__()
        self.entity = entity
        self.color = color
        self.thickness = thickness

    def on_draw(self):
        screen = self.entity.app.surfaces[LAYER_ENTITY]
        camera = self.app.scene.camera
        entity = self.entity

        world_position = pg.Vector2(
            entity.rect.x + entity.flip_offset[entity.flip_x].x,
            entity.rect.y + entity.flip_offset[entity.flip_x].y
        )
        image = entity.anim.img()
        size = image.get_size()
        rect = pg.Rect(world_position, (size[0] * camera.scale, size[1] * camera.scale))

        if not camera.is_on_screen(rect) : return

        mask = pg.mask.from_surface(self.entity.anim.img())
        outline_surface = mask.to_surface(setcolor=self.color, unsetcolor=(0, 0, 0, 0))
        outline_surface.set_colorkey((0, 0, 0))
        outline_surface = pg.transform.flip(outline_surface, self.entity.flip_x, False)

        position = self.entity.app.scene.camera.world_to_screen(world_position)

        for dx in range(-self.thickness, self.thickness + 1):
            for dy in range(-self.thickness, self.thickness + 1):
                if dx == 0 and dy == 0:
                    continue
                screen.blit(outline_surface, (position[0] + dx, position[1] + dy))
import pygame as pg

from datas.const import *

class Outline:
    def __init__(self, entity, color, thickness):
        self.entity = entity
        self.color = color
        self.thickness = thickness

    def on_draw(self):
        screen = self.entity.app.surfaces[LAYER_ENTITY]

        mask = pg.mask.from_surface(self.entity.anim.img())
        outline_surface = mask.to_surface(setcolor=self.color, unsetcolor=(0, 0, 0, 0))
        outline_surface.set_colorkey((0, 0, 0))
        outline_surface = pg.transform.flip(outline_surface, self.entity.flip_x, False)

        world_position = pg.Vector2(
            self.entity.rect.x + self.entity.flip_offset[self.entity.flip_x].x,
            self.entity.rect.y + self.entity.flip_offset[self.entity.flip_x].y
        )
        position = self.entity.app.scene.camera.world_to_screen(world_position)

        for dx in range(-self.thickness, self.thickness + 1):
            for dy in range(-self.thickness, self.thickness + 1):
                if dx == 0 and dy == 0:
                    continue
                screen.blit(outline_surface, (position[0] + dx, position[1] + dy))
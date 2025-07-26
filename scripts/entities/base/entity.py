import pygame as pg

from scripts.constants import *
from scripts.objects import GameObject

class Entity(GameObject):
    all_entities : list['Entity'] = []

    def __init__(self, name : str, rect : pg.Rect, start_action : str = "idle", invert_x : bool = False):
        super().__init__()
        Entity.all_entities.append(self)

        self.name : str = name
        self.rect : pg.Rect = rect

        self.frame_movement : pg.Vector2 = pg.Vector2()

        self.current_action : str = ""
        self.set_action(start_action)

        self.invert_x = invert_x
        self.flip_x : bool = False
        self.flip_offset : dict[bool, pg.Vector2] = {
            False : pg.Vector2(0, 0),
            True : pg.Vector2(0, 0)
        }

    def destroy(self):
        super().on_destroy()
        Entity.all_entities.remove(self)

    def set_action(self, action_name):
        if self.current_action == action_name : return

        self.current_action = action_name
        self.anim = self.app.ASSETS["animations"]["entities"][self.name][action_name].copy()

    def get_rect_points(self):
        points = []
        for point in [self.rect.topleft, self.rect.topright, self.rect.bottomleft, self.rect.bottomright]:
            points.append(pg.Vector2(point))
        return points
    
    def on_update(self):
        super().on_update()
        self.anim.update(self.app.dt)
        if self.frame_movement.x < 0:
            self.flip_x = False if self.invert_x else True
        elif self.frame_movement.x > 0:
            self.flip_x = True if self.invert_x else False

    def on_draw(self):
        super().on_draw()
        camera = self.app.scene.camera
        surface = camera.get_scaled_surface(pg.transform.flip(self.anim.img(), self.flip_x, False))
        position = camera.world_to_screen(pg.Vector2(self.rect.topleft) + self.flip_offset[self.flip_x])

        self.app.surfaces[LAYER_ENTITY].blit(surface, position)

    def on_debug_draw(self):
        super().on_debug_draw()
        camera = self.app.scene.camera

        pg.draw.rect(self.app.surfaces[LAYER_INTERFACE], "red", camera.world_rect_to_screen_rect(self.rect), width=2)
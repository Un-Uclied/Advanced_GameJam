import pygame as pg
import json

from scripts.constants import *
from scripts.objects import GameObject
from scripts.camera import *

with open("datas/projectile_data.json", 'r') as f:
    data = json.load(f)
    PROJECTILE_DATA = data

class Projectile(GameObject):
    def __init__(self, projectile_name : str,
                 start_position : pg.Vector2, start_direction : pg.Vector2,
                 time_out = 5):
        super().__init__()

        self.data = PROJECTILE_DATA[projectile_name]

        self.position = start_position
        self.direction = start_direction

        self.time_out_timer = time_out

        self.anim = self.app.ASSETS["animations"]["projectiles"][projectile_name].copy()

    def update(self):
        super().update()

        self.position += self.direction * self.data["speed"] * self.app.dt
    
        self.anim.update(self.app.dt)

        self.time_out_timer -= self.app.dt
        if self.time_out_timer <= 0:
            self.destroy()

        for rect in self.app.scene.tilemap.physic_tiles_around(self.position):
            if rect.collidepoint(self.position):
                self.destroy()
                break

    def draw(self):
        super().draw()

        surface = self.app.surfaces[LAYER_DYNAMIC]
        camera = self.app.scene.camera

        image = self.anim.img()

        angle = self.direction.angle_to(pg.Vector2(1, 0))

        rotated_img = pg.transform.rotate(image, angle)
        rotated_img = CameraView.get_scaled_surface(camera, rotated_img)

        draw_pos = self.position - pg.Vector2(rotated_img.get_size()) * 0.5
        screen_pos = CameraMath.world_to_screen(camera, draw_pos)

        surface.blit(rotated_img, screen_pos)
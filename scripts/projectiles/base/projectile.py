import pygame as pg

from datas.const import *

from scripts.objects import GameObject
from scripts.volume import Light

class Projectile(GameObject):
    all_projectiles : list['Projectile'] = []
    def __init__(self, name : str, start_position : pg.Vector2, start_direction : pg.Vector2, speed : float, time_out = 5):
        super().__init__()
        self.name = name

        self.position = start_position
        self.direction = start_direction
        self.speed = speed

        self.time_out_timer = time_out

        self.anim = self.app.ASSET_PROJECTILES[self.name].copy()

        Projectile.all_projectiles.append(self)

        self.light = Light(400, self.position)

    def destroy(self):
        super().destroy()
        self.light.destroy()
        Projectile.all_projectiles.remove(self)

    def on_update(self):
        self.position += self.direction * self.speed * self.app.dt
    
        self.anim.update(self.app.dt)

        self.light.position = self.position

        self.time_out_timer -= self.app.dt
        if self.time_out_timer <= 0:
            self.destroy()

        for rect in self.app.scene.tilemap.physic_tiles_around(self.position):
            if rect.collidepoint(self.position):
                self.destroy()

    def on_draw(self):
        super().on_draw()

        surface = self.app.surfaces[LAYER_DYNAMIC]
        camera = self.app.scene.camera

        image = self.anim.img()

        angle = -self.direction.angle_to(pg.Vector2(1, 0))

        rotated_img = pg.transform.rotate(image, angle)
        rotated_img = camera.get_scaled_surface(rotated_img)

        draw_pos = self.position - pg.Vector2(rotated_img.get_size()) * 0.5
        screen_pos = camera.world_to_screen(draw_pos)

        surface.blit(rotated_img, screen_pos)


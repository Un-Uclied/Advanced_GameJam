import pygame as pg


from .base import Entity, PhysicsEntity
from scripts.ai import WanderAI

from scripts.vfx import Outline, AnimatedParticle
from scripts.volume import Light

hit_box_size = (40, 50)

move_speed = 1.5
min_change_timer = .8
max_change_timer = 1.5

class Soul(PhysicsEntity):
    all_souls : list['Soul'] = []
    def __init__(self, spawn_position : pg.Vector2):
        self.outline = Outline(self, "red")
        
        rect = pg.Rect(spawn_position, hit_box_size)
        super().__init__("soul", rect)

        self.ai = WanderAI(self, move_speed, min_change_timer, max_change_timer)

        self.flip_offset = {
            False: pg.Vector2(5, -20),
            True: pg.Vector2(5, -20)
        }

        self.light = Light(250, pg.Vector2(self.rect.center))
        self.light_follow_speed = 5

    def on_destroy(self):
        super().on_destroy()
        self.light.on_destroy()
        self.outline.on_destroy()

        AnimatedParticle("soul_collect", pg.Vector2(self.rect.center))
        self.app.ASSETS["sounds"]["soul"]["interact"].play()

    def follow_light(self):
        self.light.position = self.light.position.lerp(self.rect.center, max(min(self.app.dt * self.light_follow_speed, 1), 0))

    def handle_input(self):
        for event in self.app.events:
            if event.type == pg.KEYDOWN and event.key == pg.K_e and self.rect.colliderect(self.app.scene.pc.rect):
                self.app.scene.camera.shake(10)
                self.on_destroy()

    def on_update(self):
        super().on_update()

        self.ai.on_update()

        self.velocity.x = self.ai.direction.x * self.ai.move_speed * 100

        self.follow_light()

        self.handle_input()
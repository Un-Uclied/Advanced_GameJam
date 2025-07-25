import pygame as pg

from .base.entity import Entity
from .base.physics_entity import PhysicsEntity

from .soul import Soul

from scripts.volume import Outline, Light

hit_box_size = (48, 128)

class PlayerCharacter(PhysicsEntity):
    def __init__(self, spawn_position : pg.Vector2):
        self.outline = Outline(self, "red")

        rect = pg.Rect(spawn_position, hit_box_size)
        super().__init__("player", rect)

        self.input_drection = pg.Vector2()

        self.move_speed = 4.6
        self.jump_power = -9.5

        self.jump_count = 2
        self.current_jump_count = 0

        self.is_accel = False

        self.accel_power = 7
        self.deccel_power = 5
        self.lerped_movement = pg.Vector2()

        self.flip_offset = {
            False : pg.Vector2(0, 0),
            True : pg.Vector2(-40, 0)
        }

        self.light = Light(500, pg.Vector2(self.rect.center))
        self.light_follow_speed = 3

        self.camera_follow_speed = 5

    def get_input(self):
        key = pg.key.get_pressed()
        self.input_drection = pg.Vector2()
        if key[pg.K_a]:
            self.input_drection.x = -1
        if key[pg.K_d]:
            self.input_drection.x = 1
        if key[pg.K_w]:
            self.input_drection.y = 1
        if key[pg.K_s]:
            self.input_drection.y = -1
        self.is_accel = bool(self.input_drection.x)
        
        for event in self.app.events:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.jump()
                if event.key == pg.K_e:
                    for entity in Entity.all_entities:
                        if entity is not self and isinstance(entity, Soul) and self.rect.colliderect(entity.rect):
                            entity.destroy()
                            self.app.scene.camera.shake(20)

    def control_animation(self):
        if not self.collisions["down"]:
            self.set_action("jump")
        else:
            if self.is_accel:
                self.set_action("run")
            else : self.set_action("idle")

    def jump(self):
        if (self.current_jump_count >= self.jump_count): return
        self.current_gravity = self.jump_power * 100
        self.current_jump_count += 1
        self.app.ASSET_SFXS["player"]["jump"].play()

    def physics_movement(self):
        self.lerped_movement = self.lerped_movement.lerp(
            pg.Vector2(self.input_drection.x * self.move_speed * 100, 0),
            max(min((self.accel_power if self.is_accel else self.deccel_power) * self.app.dt, 1), 0)
        )

        self.frame_movement = pg.Vector2(self.velocity.x + self.lerped_movement.x, self.velocity.y + self.current_gravity)
        self.velocity = self.velocity.lerp(pg.Vector2(0, 0), max(min(self.app.dt * self.drag_vel, 1), 0))

    def destroy(self):
        super().destroy()
        self.light.destroy()
        self.outline.destroy()

    def follow_light_and_camera(self):
        camera = self.app.scene.camera
        target_pos = self.rect.center

        camera.offset = camera.offset.lerp(target_pos, max(min(self.app.dt * self.camera_follow_speed, 1), 0))
        self.light.position = self.light.position.lerp(target_pos, max(min(self.app.dt * self.light_follow_speed, 1), 0))

    def on_update(self):
        self.get_input()
        super().on_update()
        self.control_animation()
        self.follow_light_and_camera()
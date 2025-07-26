import pygame as pg

from .base import PhysicsEntity

from scripts.projectiles import PlayerProjectile
from scripts.volume import Light
from scripts.vfx import Outline

hit_box_size = (48, 128)
projectile_damage = 25

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

    def handle_input(self):
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

            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.projectile_attack()

    def control_animation(self):
        if not self.collisions["down"]:
            self.set_action("jump")
        else:
            if self.is_accel:
                self.set_action("run")
            else : self.set_action("idle")

    def projectile_attack(self):
        camera = self.app.scene.camera

        plr_pos = pg.Vector2(self.rect.center)
        direction = (camera.screen_to_world(pg.Vector2(pg.mouse.get_pos())) - plr_pos).normalize()
        PlayerProjectile(self.name, projectile_damage, plr_pos, direction)

    def jump(self):
        if (self.current_jump_count >= self.jump_count): return
        self.current_gravity = self.jump_power * 100
        self.current_jump_count += 1

        self.app.ASSETS["sounds"]["player"]["jump"].play()

    def physics_movement(self):
        self.lerped_movement = self.lerped_movement.lerp(
            pg.Vector2(self.input_drection.x * self.move_speed * 100, 0),
            max(min((self.accel_power if self.is_accel else self.deccel_power) * self.app.dt, 1), 0)
        )

        self.frame_movement = pg.Vector2(self.velocity.x + self.lerped_movement.x, self.velocity.y + self.current_gravity)
        self.velocity = self.velocity.lerp(pg.Vector2(0, 0), max(min(self.app.dt * self.drag_vel, 1), 0))

    def on_destroy(self):
        super().on_destroy()
        self.light.on_destroy()
        self.outline.on_destroy()

    def follow_light_and_camera(self):
        camera = self.app.scene.camera
        target_pos = self.rect.center

        camera.position = camera.position.lerp(target_pos, max(min(self.app.dt * self.camera_follow_speed, 1), 0))
        self.light.position = self.light.position.lerp(target_pos, max(min(self.app.dt * self.light_follow_speed, 1), 0))

    def on_update(self):
        self.handle_input()
        super().on_update()
        self.control_animation()
        self.follow_light_and_camera()
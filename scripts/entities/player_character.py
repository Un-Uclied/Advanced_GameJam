import pygame as pg

from .base import PhysicsEntity, VELOCITY_DRAG

from scripts.camera import *
from scripts.projectiles import PlayerProjectile
from scripts.volume import Light
from scripts.vfx import Outline

hit_box_size = (48, 128)
projectile_damage = 25

MOVE_SPEED = 3.25*4
JUMP_POWER = -7.5

MAX_JUMP_COUNT = 2

ACCEL_POWER = 7
DECCEL_POWER = 5

LIGHT_FOLLOW_SPEED = 3
CAMERA_FOLLOW_SPEED = 5

LIGHT_SIZE = 500

class PlayerCharacter(PhysicsEntity):
    def __init__(self, spawn_position : pg.Vector2):
        
        self.outline = Outline(self, "red")

        rect = pg.Rect(spawn_position, hit_box_size)
        super().__init__("player", rect)

        self.input_drection = pg.Vector2()

        self.current_jump_count = 0

        self.is_accel = False

        self.lerped_movement = pg.Vector2()

        self.flip_offset = {
            False : pg.Vector2(0, 0),
            True : pg.Vector2(-40, 0)
        }

        self.light = Light(LIGHT_SIZE, pg.Vector2(self.rect.center))

    def destroy(self):
        self.light.destroy()
        self.outline.destroy()
        super().destroy()

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
        direction = (CameraMath.screen_to_world(camera, pg.Vector2(pg.mouse.get_pos())) - plr_pos).normalize()
        PlayerProjectile(plr_pos, direction)

    def jump(self):
        if (self.current_jump_count >= MAX_JUMP_COUNT): return
        self.current_gravity = JUMP_POWER * 100
        self.current_jump_count += 1

        self.app.ASSETS["sounds"]["player"]["jump"].play()

    def physics_gravity(self):
        super().physics_gravity()
        if self.collisions["down"]:
            self.current_jump_count = 0

    def physics_movement(self):
        self.lerped_movement = self.lerped_movement.lerp(
            pg.Vector2(self.input_drection.x * MOVE_SPEED * 100, 0),
            max(min((ACCEL_POWER if self.is_accel else DECCEL_POWER) * self.app.dt, 1), 0)
        )

        self.frame_movement = pg.Vector2(self.velocity.x + self.lerped_movement.x, self.velocity.y + self.current_gravity)
        self.velocity = self.velocity.lerp(pg.Vector2(0, 0), max(min(self.app.dt * VELOCITY_DRAG, 1), 0))

    def follow_light_and_camera(self):
        camera = self.app.scene.camera
        target_pos = self.rect.center

        camera.position = camera.position.lerp(target_pos, max(min(self.app.dt * CAMERA_FOLLOW_SPEED, 1), 0))
        self.light.position = self.light.position.lerp(target_pos, max(min(self.app.dt * LIGHT_FOLLOW_SPEED, 1), 0))

    def update(self):
        self.handle_input()
        super().update()
        self.control_animation()
        self.follow_light_and_camera()
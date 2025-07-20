import pygame as pg

from datas.const import *
from .animation import *
from .objects import *

class Entity(GameObject):
    def __init__(self, name : str, rect : pg.FRect):
        super().__init__()
        self.name : str = name
        self.rect : pg.Rect = rect

        self.velocity : pg.Vector2 = pg.Vector2()
        self.frame_movement : pg.Vector2 = pg.Vector2()

        self.current_action : str = ""
        self.set_action("idle")

        self.flip_x : bool = False
        self.flip_offset : dict[bool, pg.Vector2] = {
            False : pg.Vector2(0, 0),
            True : pg.Vector2(0, 0)
        }

    def set_action(self, action_name):
        if self.current_action == action_name : return
        self.current_action = action_name
        self.anim = self.app.ASSET_ANIMATIONS[self.name][action_name].copy()

    def get_center_pos(self):
        return pg.Vector2(self.rect.x + self.rect.width / 2, self.rect.y + self.rect.height / 2)
    
    def on_update(self):
        super().on_update()
        self.anim.update()
        if self.frame_movement.x < 0:
            self.flip_x = True
        elif self.frame_movement.x > 0:
            self.flip_x = False

    def _debug_draw(self):
        pos = self.app.scene.camera.world_to_screen(pg.Vector2(self.rect.x, self.rect.y))

        screen = self.app.surfaces[LAYER_ENTITY]
        pg.draw.rect(screen, "red", pg.FRect(pos.x, pos.y, self.rect.w * self.app.scene.camera.scale, self.rect.h * self.app.scene.camera.scale), width=2)

    def on_draw(self):
        super().on_draw()
        camera = self.app.scene.camera
        surface = pg.transform.flip(self.anim.img(), self.flip_x, False)
        world_position = pg.Vector2(self.rect.x + self.flip_offset[self.flip_x].x, self.rect.y + self.flip_offset[self.flip_x].y)

        screen = self.app.surfaces[LAYER_ENTITY]
        screen.blit(camera.get_scaled_surface(surface), camera.world_to_screen(world_position))

        self._debug_draw()

class PhysicsEntity(Entity):
    def __init__(self, name, rect : pg.Rect):
        super().__init__(name, rect)

        self.collisions = {"left" : False, "right" : False, "up" : False, "down" : False}

        self.max_gravtity = 28
        self.gravity_strength = 22

    def _physics_collision(self):
        self.collisions = {"left" : False, "right" : False, "up" : False, "down" : False}
        #충돌
        self.rect.x += int(self.frame_movement.x)
        for rect in self.app.scene.tilemap.physic_tiles_around(self.get_center_pos()):
            if rect.colliderect(self.rect):
                #right
                if (self.frame_movement.x > 0):
                    self.collisions["right"] = True
                    self.rect.x = rect.x - rect.width
                #left
                if (self.frame_movement.x < 0):
                    self.collisions["left"] = True
                    self.rect.x = rect.x + self.rect.width

        self.rect.y += self.frame_movement.y
        for rect in self.app.scene.tilemap.physic_tiles_around(self.get_center_pos()):
            if rect.colliderect(self.rect):
                #down
                if (self.frame_movement.y > 0):
                    self.collisions["down"] = True
                    self.rect.y = rect.y - self.rect.height
                #up
                if (self.frame_movement.y < 0):
                    self.collisions["up"] = True
                    self.rect.y = rect.y + rect.height
       
    def _physics_gravity(self):   
        #중력
        if (self.collisions["down"]):
            self.velocity.y = .001
            self.current_jump_count = 0
        else:
            self.velocity.y = min(self.max_gravtity, self.velocity.y + self.app.dt * self.gravity_strength)
            
        #머리박으면 빠르게 나올수 있음
        if (self.collisions["up"]):
            self.velocity.y = 0

    def _physics_movement(self):
        self.frame_movement = pg.Vector2(self.velocity.x, self.velocity.y)  

    def on_update(self):
        super().on_update()
        self._physics_movement()
        self._physics_collision()
        self._physics_gravity()

class Player(PhysicsEntity):
    def __init__(self, name : str = "player", rect : pg.Rect = pg.FRect(0, 0, 80, 100)):
        super().__init__(name, rect)
        self.input_drection = pg.Vector2()

        self.move_speed = 4.2
        self.jump_power = -8

        self.jump_count = 2
        self.current_jump_count = 0

        self.is_accel = False

        self.accel_power = 12
        self.deccel_power = 7
        self.lerped_movement = pg.Vector2()

        self.flip_offset = {
            False : pg.Vector2(0, 0),
            True : pg.Vector2(-40, 0)
        }

    def _get_input(self):
        key = pg.key.get_pressed()
        self.input_drection.x = 0
        if key[pg.K_a]:
            self.input_drection.x = -1
        if key[pg.K_d]:
            self.input_drection.x = 1
        self.is_accel = bool(self.input_drection.x)
        
        for event in self.app.events:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self._jump()

    def _control_animation(self):
        if not self.collisions["down"]:
            self.set_action("jump")
        else:
            if self.is_accel:
                self.set_action("run")
            else : self.set_action("idle")

    def _jump(self):
        if (self.current_jump_count >= self.jump_count): return
        self.velocity.y = self.jump_power
        self.current_jump_count += 1

    def _physics_movement(self):
        self.lerped_movement = self.lerped_movement.lerp(
            pg.Vector2(self.input_drection.x * self.move_speed, 0),
            max(min(self.app.dt * (self.accel_power if self.is_accel else self.deccel_power), 1), 0)
        )

        self.frame_movement = pg.Vector2(self.lerped_movement.x, self.velocity.y)

    def on_update(self):
        self._get_input()
        super().on_update()
        self._control_animation()
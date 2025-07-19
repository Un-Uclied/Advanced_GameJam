import pygame as pg

from .animation import *
from .objects import *

class Entity(GameObject):
    def __init__(self, name : str, rect : pg.Rect):
        super().__init__()
        self.name = name
        self.rect = rect

        self.velocity = pg.Vector2()
        self.frame_movement = pg.Vector2()

        self.current_action = ""
        self.set_action("idle")

    def set_action(self, action_name):
        if self.current_action == action_name : return
        self.current_action = action_name
        self.anim = self.app.ANIMATIONS[self.name][action_name].copy()

    def get_center_pos(self):
        return pg.Vector2(self.rect.x + self.rect.width / 2, self.rect.y + self.rect.height / 2)
    
    def on_update(self):
        super().on_update()
        self.anim.update()

    def on_draw(self):
        super().on_draw()
        self.app.scene.camera.blit(self.anim.img(), pg.Vector2(self.rect.x, self.rect.y), 2)

class PhysicsEntity(Entity):
    def __init__(self, name, rect : pg.Rect):
        super().__init__(name, rect)

        self.collisions = {"left" : False, "right" : False, "up" : False, "down" : False}

        self.max_gravtity = 18
        self.gravity_strength = 12

        self.isAccel = False

    def _physics_collistion(self):
        self.collisions = {"left" : False, "right" : False, "up" : False, "down" : False}
        #충돌
        self.rect.x += self.frame_movement.x
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
        self._physics_collistion()
        self._physics_gravity()

class Player(PhysicsEntity):
    def __init__(self, name : str = "player", rect : pg.Rect = pg.Rect(18, 24, 0, 0)):
        super().__init__(name, rect)
        self.input_drection = pg.Vector2()

        self.move_speed = 4.2
        self.jump_power = -12
        self.jump_count = 2
        self.current_jump_count = 0
        
        self.move_accel = 12
        self.move_deccel = 7
        self.lerpedMovement = pg.Vector2()

    def _get_input(self):
        key = pg.key.get_pressed()
        if (key[pg.K_a]):
            self.input_drection.x = -1
            self.isAccel = True
        if (key[pg.K_d]):
            self.input_drection.x = 1
            self.isAccel = True
        if (not key[pg.K_a] and not key[pg.K_d]):
            self.input_drection.x = 0
            self.isAccel = False

        if (key[pg.K_w]):
            self.input_drection.y = -1
        if (key[pg.K_s]):
            self.input_drection.y = 1
        if (not key[pg.K_w] and not key[pg.K_s]):
            self.input_drection.y = 0
        
        for event in self.app.events:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.jump()

    def jump(self):
        if (self.current_jump_count >= self.jump_count): return
        self.velocity.y = self.jump_power
        self.current_jump_count += 1

    def _physics_movement(self):
        # 가속 감속
        if self.isAccel:
            self.lerpedMovement.lerp(pg.Vector2(self.input_drection.x * self.move_speed, 0), self.app.dt * self.move_accel)
        else:
            self.lerpedMovement.lerp(pg.Vector2(self.input_drection.x * self.move_speed, 0), self.app.dt * self.move_deccel)

        self.frame_movement = pg.Vector2(self.lerpedMovement.x + self.velocity.x, self.velocity.y)

    def on_update(self):
        self._get_input()
        super().on_update()
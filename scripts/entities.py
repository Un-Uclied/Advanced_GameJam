import pygame as pg

from datas.const import *
from .animation import *
from .objects import *
from .volume import Light2D
from .outline import *
from .ai import *
from .status import *

DEFAULT_GRAVITY = 300

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
        super().destroy()
        Entity.all_entities.remove(self)

    def set_action(self, action_name):
        if self.current_action == action_name : return

        self.current_action = action_name
        self.anim = self.app.ASSET_ANIMATIONS[self.name][action_name].copy()

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

class PhysicsEntity(Entity):
    def __init__(self, name, rect : pg.Rect, start_action : str = "idle", invert_x : bool = False):
        super().__init__(name, rect, start_action, invert_x)

        self.collisions = {"left" : False, "right" : False, "up" : False, "down" : False}

        self.velocity : pg.Vector2 = pg.Vector2()
        self.drag_vel = 10

        self.max_gravtity = 1000
        self.gravity_strength = 28
        self.current_gravity = DEFAULT_GRAVITY

    def physics_collision(self):
        self.collisions = {"left" : False, "right" : False, "up" : False, "down" : False}

        self.rect.x += int(self.frame_movement.x * self.app.dt)
        for point in self.get_rect_points():
            for rect in self.app.scene.tilemap.physic_tiles_around(point):
                if rect.colliderect(self.rect):
                    if (self.frame_movement.x > 0):
                        self.collisions["right"] = True
                        self.frame_movement.x = 0
                        self.rect.right = rect.x
                    if (self.frame_movement.x < 0):
                        self.collisions["left"] = True
                        self.frame_movement.x = 0
                        self.rect.x = rect.right

        self.rect.y += int(self.frame_movement.y * self.app.dt)
        for point in self.get_rect_points():
            for rect in self.app.scene.tilemap.physic_tiles_around(point):
                if rect.colliderect(self.rect):
                    if (self.frame_movement.y > 0):
                        self.collisions["down"] = True
                        self.rect.bottom =rect.y

                    if (self.frame_movement.y < 0):
                        self.collisions["up"] = True
                        self.rect.top = rect.bottom
                    
    def physics_gravity(self):   
        #중력
        if (self.collisions["down"]):
            self.current_gravity = DEFAULT_GRAVITY
            self.current_jump_count = 0
        else:
            self.current_gravity = min(self.max_gravtity * self.app.dt * 100, self.current_gravity + self.gravity_strength * self.app.dt * 100)
            
        if (self.collisions["up"]):
            self.current_gravity = 0

    def physics_movement(self):
        self.frame_movement = pg.Vector2(self.velocity.x, self.velocity.y + self.current_gravity)  
        self.velocity = self.velocity.lerp(pg.Vector2(0, 0), max(min(self.app.dt * self.drag_vel, 1), 0))

    def on_update(self):
        super().on_update()
        self.physics_movement()
        self.physics_collision()
        self.physics_gravity()

class Player(PhysicsEntity):
    def __init__(self, rect : pg.Rect = pg.Rect(0, 0, 80, 100)):
        self.outline = Outline(self, "red")
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

        self.light = Light2D(500, pg.Vector2(self.rect.center))
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

class Soul(PhysicsEntity):
    def __init__(self, rect: pg.Rect = pg.Rect(0, 0, 40, 50)):
        self.outline = Outline(self, "red")
        super().__init__("soul", rect)
        self.ai = WanderAI(self, move_speed=1.5)

        self.flip_offset = {
            False: pg.Vector2(5, -20),
            True: pg.Vector2(5, -20)
        }

        self.light = Light2D(250, pg.Vector2(self.rect.center))
        self.light_follow_speed = 5

    def destroy(self):
        super().destroy()
        self.light.destroy()
        self.outline.destroy()

    def follow_light(self):
        self.light.position = self.light.position.lerp(self.rect.center, max(min(self.app.dt * self.light_follow_speed, 1), 0))

    def on_update(self):
        super().on_update()

        self.ai.on_update()

        self.velocity.x = self.ai.direction.x * self.ai.move_speed * 100

        self.follow_light()

class Portal(Entity):
    def __init__(self, rect : pg.Rect = pg.Rect(0, 0, 75, 75)):
        super().__init__("portal", rect)

        self.light = Light2D(500, pg.Vector2(self.rect.center), 50)
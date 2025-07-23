import pygame as pg

from datas.const import *
from .animation import *
from .objects import *
from .volume import Light2D

DEFAULT_GRAVITY = 300

class Entity(GameObject):
    def __init__(self, name : str, rect : pg.Rect):
        super().__init__()
        self.name : str = name
        self.rect : pg.Rect = rect

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

    def get_rect_points(self):
        points = []
        for point in [self.rect.topleft, self.rect.topright, self.rect.bottomleft, self.rect.bottomright]:
            points.append(pg.Vector2(point))
        return points
    
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
        pg.draw.rect(screen, "red", pg.Rect(pos.x, pos.y, self.rect.w * self.app.scene.camera.scale, self.rect.h * self.app.scene.camera.scale), width=2)

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

        self.velocity : pg.Vector2 = pg.Vector2()
        self.drag_vel = 10

        self.max_gravtity = 1000
        self.gravity_strength = 28
        self.current_gravity = DEFAULT_GRAVITY

    def _physics_collision(self):
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
                    
    def _physics_gravity(self):   
        #중력
        if (self.collisions["down"]): #북 따닥 따닥따닥
            self.current_gravity = DEFAULT_GRAVITY #왜 그런건진 모르겠는데 "딱" 125이상이여야 충돌에서 이상하게 안되더라;; 일단 125말고 다른 수로 초반 중력 설정하긴 할건데 진짜 왜이럼;
            self.current_jump_count = 0 #아 설마 125 * 8이 딱 1000이라서 그런건가
        else:
            self.current_gravity = min(self.max_gravtity * self.app.dt * 1000, self.current_gravity + self.gravity_strength * self.app.dt * 100)
            
        #머리박으면 빠르게 나올수 있음
        if (self.collisions["up"]):
            self.current_gravity = 0

    def _physics_movement(self):
        self.frame_movement = pg.Vector2(self.velocity.x, self.velocity.y + self.current_gravity)  
        self.velocity = self.velocity.lerp(pg.Vector2(0, 0), max(min(self.app.dt * self.drag_vel, 1), 0))

    def on_update(self):
        super().on_update()
        self._physics_movement()
        self._physics_collision()
        self._physics_gravity()

class Player(PhysicsEntity):
    def __init__(self, name : str = "player", rect : pg.Rect = pg.Rect(0, 0, 80, 100)):
        super().__init__(name, rect)
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

        self.light = Light2D(360, pg.Vector2(self.rect.center))

        self.camera_follow_speed = 5
        self.light_follow_speed = 3

    def _get_input(self):
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
        self.current_gravity = self.jump_power * 100
        self.current_jump_count += 1

    def _physics_movement(self):
        self.lerped_movement = self.lerped_movement.lerp(
            pg.Vector2(self.input_drection.x * self.move_speed * 100, 0),
            max(min((self.accel_power if self.is_accel else self.deccel_power) * self.app.dt, 1), 0) #wtf??
        )

        self.frame_movement = pg.Vector2(self.velocity.x + self.lerped_movement.x, self.velocity.y + self.current_gravity)
        self.velocity = self.velocity.lerp(pg.Vector2(0, 0), max(min(self.app.dt * self.drag_vel, 1), 0))

    def on_update(self):
        self._get_input()
        super().on_update()
        self._control_animation()

        camera = self.app.scene.camera
        light = self.light
        target_pos = self.rect.center

        camera.offset = camera.offset.lerp(target_pos, max(min(self.app.dt * self.camera_follow_speed, 1), 0))
        light.position = light.position.lerp(target_pos, max(min(self.app.dt * self.light_follow_speed, 1), 0))
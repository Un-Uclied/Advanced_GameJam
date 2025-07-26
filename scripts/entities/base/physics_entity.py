import pygame as pg

from .entity import Entity

DEFAULT_GRAVITY = 300
MAX_GRAVITY = 1000
GRAVITY_STRENGTH = 28

VELOCITY_DRAG = 10

class PhysicsEntity(Entity):
    def __init__(self, name, rect : pg.Rect, start_action : str = "idle", invert_x : bool = False):
        super().__init__(name, rect, start_action, invert_x)

        self.collisions = {"left" : False, "right" : False, "up" : False, "down" : False}

        self.velocity : pg.Vector2 = pg.Vector2()

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
        if (self.collisions["down"]):
            self.current_gravity = DEFAULT_GRAVITY
        else:
            self.current_gravity = min(MAX_GRAVITY * self.app.dt * 100, self.current_gravity + GRAVITY_STRENGTH * self.app.dt * 100)
            
        if (self.collisions["up"]):
            self.current_gravity = 0

    def physics_movement(self):
        self.frame_movement = pg.Vector2(self.velocity.x, self.velocity.y + self.current_gravity)  
        self.velocity = self.velocity.lerp(pg.Vector2(0, 0), max(min(self.app.dt * VELOCITY_DRAG, 1), 0))

    def on_update(self):
        super().on_update()
        self.physics_movement()
        self.physics_collision()
        self.physics_gravity()
import pygame as pg
import random

from scripts.entities import PlayerCharacter

class AI:
    def __init__(self, entity):
        self.entity = entity
        self.direction = pg.Vector2(0, 0)

    def on_update(self):
        pass

class WanderAI(AI):
    def __init__(self, entity, move_speed=1.5, min_change_timer = .8, max_change_timer = 1.5):
        super().__init__(entity)
        
        self.direction.x = random.choice([-1, 0, 1])
        self.direction.y = 0
    
        self.move_speed = move_speed

        self.min_change_timer = min_change_timer
        self.max_change_timer = max_change_timer
        self.current_change_timer = random.uniform(self.min_change_timer, self.max_change_timer)

        self.fix_direction_timer = 0.6
    
    def check_floor(self):
        entity = self.entity
        tilemap = entity.app.scene.tilemap
        tile_size = tilemap.tile_size
        check_w = 4

        left = pg.Vector2(entity.rect.midbottom[0] - tile_size // 2 + check_w, entity.rect.bottom + 1)
        right = pg.Vector2(entity.rect.midbottom[0] + tile_size // 2 - check_w, entity.rect.bottom + 1)

        if not any(r.collidepoint(left) for r in tilemap.physic_tiles_around(left)):
            self.handle_collision_or_fall("fall_left")
        elif not any(r.collidepoint(right) for r in tilemap.physic_tiles_around(right)):
            self.handle_collision_or_fall("fall_right")

    def check_wall(self):
        entity = self.entity
        if entity.collisions["right"]:
            self.handle_collision_or_fall("hit_right")
        elif entity.collisions["left"]:
            self.handle_collision_or_fall("hit_left")

    def on_update(self):
        super().on_update()

        dt = self.entity.app.dt
        
        self.check_floor()
        self.check_wall()

        if self.fix_direction_timer > 0:
            self.fix_direction_timer -= dt
        else:
            if self.current_change_timer > 0:
                self.current_change_timer -= dt
            else:
                self.current_change_timer = random.uniform(self.min_change_timer, self.max_change_timer)
                self.direction.x = random.choice([-1, 0, 1])

    def handle_collision_or_fall(self, event_type):
        if event_type == "fall_left":
            self.direction.x = 1
        elif event_type == "fall_right":
            self.direction.x = -1
        elif event_type == "hit_left":
            self.direction.x = 1
        elif event_type == "hit_right":
            self.direction.x = -1
        self.fix_direction_timer = 0.6

class ChaseAI(AI):
    def __init__(self, entity, follow_speed: float, max_follow_range: float):
        super().__init__(entity)

        self.max_follow_range = max_follow_range
        self.follow_speed = follow_speed

        self.can_follow = True

        self.start_positon = pg.Vector2(self.entity.rect.center)
        self.target_position = self.start_positon

    def on_update(self):
        super().on_update()
        entity = self.entity
        dt = entity.app.dt
        pc = PlayerCharacter.singleton

        entity_center = pg.Vector2(entity.rect.center)
        player_center = pg.Vector2(pc.rect.center)
        current_distance = entity_center.distance_to(player_center)

        if current_distance <= self.max_follow_range:
            self.target_position = player_center
        else:
            self.target_position = self.start_positon

        if self.can_follow:
            self.direction = self.target_position - entity_center
            if self.direction.length_squared() > 0:
                self.direction = self.direction.normalize()
                entity.frame_movement = self.direction * self.follow_speed

                entity.rect.x += entity.frame_movement.x * dt
                entity.rect.y += entity.frame_movement.y * dt
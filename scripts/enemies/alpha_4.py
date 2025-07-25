import pygame as pg

from datas.const import *

from .base import WanderEnemy

hit_box_size = (80, 165)

normal_walk_speed = 1.5
normal_min_change_timer = 1
normal_max_change_timer = 1.8

crazy_range = 500

crazy_walk_speed = 6
crazy_min_change_timer = 2
crazy_max_change_timer = 3

class FourAlpha(WanderEnemy):
    def __init__(self, spawn_position : pg.Vector2):
        rect = pg.Rect(spawn_position, hit_box_size)
        super().__init__(FOUR_ALPHA, rect,
                          max_health=175,
                          attack_damage=25, 
                          move_speed=normal_walk_speed, 
                          min_change_timer=normal_min_change_timer, 
                          max_change_timer=normal_max_change_timer)

        self.flip_offset = {
            False: pg.Vector2(-20, -13),
            True: pg.Vector2(-20, -13)
        }

    def on_update(self):
        pc = self.app.scene.pc

        entity_center = pg.Vector2(self.rect.center)
        player_center = pg.Vector2(pc.rect.center)
        current_distance = entity_center.distance_to(player_center)

        if current_distance < crazy_range:
            self.ai.move_speed = crazy_walk_speed
            self.ai.min_change_timer = crazy_max_change_timer
            self.ai.max_change_timer = crazy_max_change_timer
        else:
            self.ai.move_speed = normal_walk_speed
            self.ai.min_change_timer = normal_max_change_timer
            self.ai.max_change_timer = normal_max_change_timer

        super().on_update()
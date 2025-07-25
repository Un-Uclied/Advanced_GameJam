from datas.const import *

from .base import WanderEnemy

hit_box_size = (110, 110)

class OneAlpha(WanderEnemy):
    def __init__(self, spawn_position : pg.Vector2):
        rect = pg.Rect(spawn_position, hit_box_size)
        super().__init__(ONE_ALPHA, rect,
                         max_health=100,
                         attack_damage=5,
                         move_speed=2.2,
                         min_change_timer=1, 
                         max_change_timer=1.8)

        self.flip_offset = {
            False: pg.Vector2(0, -12),
            True: pg.Vector2(0, -12)
        }
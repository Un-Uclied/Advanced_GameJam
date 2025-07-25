from datas.const import *

from .base import WanderEnemy

hit_box_size = (110, 110)

class FiveOmega(WanderEnemy):
    def __init__(self, spawn_position : pg.Vector2):
        rect = pg.Rect(spawn_position, hit_box_size)
        super().__init__(FIVE_OMEGA, rect, 
                        max_health=999,
                        attack_damage=999,
                        move_speed=999, 
                        min_change_timer=.1,
                        max_change_timer=.2)
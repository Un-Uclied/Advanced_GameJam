from datas.const import *

from .base import GhostEnemy

hit_box_size = (110, 110)

class ThreeAlpha(GhostEnemy):
    def __init__(self, spawn_position : pg.Vector2):
        rect = pg.Rect(spawn_position, hit_box_size)
        super().__init__(THREE_ALPHA, rect, 
                         follow_speed=200, 
                         max_follow_range=400, 
                         attack_damage=20, 
                         max_attack_time=1.2)
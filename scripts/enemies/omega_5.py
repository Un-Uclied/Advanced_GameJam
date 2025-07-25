from datas.const import *

from .base.wander_enemy import WanderEnemy

hit_box_size = (110, 110)

move_speed = 2.2
min_change_timer = 1
max_change_timer = 1.8

attack_damage = 9999999999

class FiveOmega(WanderEnemy):
    def __init__(self, spawn_position : pg.Vector2):
        rect = pg.Rect(spawn_position, hit_box_size)
        super().__init__(FIVE_OMEGA, rect, attack_damage, move_speed, min_change_timer, max_change_timer)
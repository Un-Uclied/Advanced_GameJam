import json

from scripts.constants import *
from scripts.projectiles import ProjectileAlpha
from .base import ProjectileEnemy

ENEMY_NAME = "two_alpha"
with open("datas/enemy_data.json", 'r') as f:
    data = json.load(f)[ENEMY_NAME]
    HIT_BOX_SIZE = tuple(data["hit_box_size"])
    FIRE_RANGE = data["fire_range"]
    FIRE_COOLTIME = data["fire_cooltime"]
    MIN_CHANGE_TIMER = data["min_change_timer"]
    MAX_CHANGE_TIMER = data["max_change_timer"]
    FLIP_OFFSET = pg.Vector2(data["flip_offset"])
    
class TwoAlpha(ProjectileEnemy):
    def __init__(self, spawn_position : pg.Vector2):
        super().__init__(
                         name=ENEMY_NAME,
                         rect=pg.Rect(spawn_position, HIT_BOX_SIZE),
                         fire_range=FIRE_RANGE,
                         fire_cooltime=FIRE_COOLTIME,
                         projectile_class=ProjectileAlpha,
                         min_change_timer=MIN_CHANGE_TIMER, 
                         max_change_timer=MAX_CHANGE_TIMER)

        self.flip_offset = {
            False: FLIP_OFFSET,
            True: FLIP_OFFSET
        }
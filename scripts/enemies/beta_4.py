import json

from scripts.constants import *
from .base import WanderEnemy

ENEMY_NAME = "four_beta"
with open("datas/enemy_data.json", 'r') as f:
    data = json.load(f)[ENEMY_NAME]
    HIT_BOX_SIZE = tuple(data["hit_box_size"])
    MIN_CHANGE_TIMER = data["min_change_timer"]
    MAX_CHANGE_TIMER = data["max_change_timer"]
    FLIP_OFFSET = pg.Vector2(data["flip_offset"])
    
class FourBeta(WanderEnemy):
    def __init__(self, spawn_position : pg.Vector2):
        super().__init__(
                         name=ENEMY_NAME,
                         rect=pg.Rect(spawn_position, HIT_BOX_SIZE),
                         min_change_timer=MIN_CHANGE_TIMER, 
                         max_change_timer=MAX_CHANGE_TIMER)

        self.flip_offset = {
            False: FLIP_OFFSET,
            True: FLIP_OFFSET
        }
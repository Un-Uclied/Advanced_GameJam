import json

from scripts.constants import *
from .base import GhostEnemy

ENEMY_NAME = "three_alpha"
with open("datas/enemy_data.json", 'r') as f:
    data = json.load(f)[ENEMY_NAME]
    HIT_BOX_SIZE = tuple(data["hit_box_size"])
    MAX_FOLLOW_RANGE = data["max_follow_range"]
    MAX_ATTACK_TIME = data["max_attack_time"]

class ThreeAlpha(GhostEnemy):
    def __init__(self, spawn_position : pg.Vector2):
        super().__init__(
                         name=ENEMY_NAME,
                         rect=pg.Rect(spawn_position, HIT_BOX_SIZE),
                         max_follow_range=MAX_FOLLOW_RANGE,
                         max_attack_time=MAX_ATTACK_TIME)
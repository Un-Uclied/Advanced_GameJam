import json
import random

from scripts.constants import *
from .base import GhostEnemy

ENEMY_NAME = "three_beta"
with open("datas/enemy_data.json", 'r') as f:
    data = json.load(f)[ENEMY_NAME]
    HIT_BOX_SIZE = tuple(data["hit_box_size"])
    MAX_FOLLOW_RANGE = data["max_follow_range"]
    MAX_ATTACK_TIME = data["max_attack_time"]
    X_RANDOM = data["max_tp_x_random"]
    Y_RANDOM = data["max_tp_y_random"]

class ThreeBeta(GhostEnemy):
    def __init__(self, spawn_position : pg.Vector2):
        super().__init__(
                         name=ENEMY_NAME,
                         rect=pg.Rect(spawn_position, HIT_BOX_SIZE),
                         max_follow_range=MAX_FOLLOW_RANGE,
                         max_attack_time=MAX_ATTACK_TIME)
        
    def attack(self):
        ps = self.app.scene.player_status
        pc = ps.player_character

        pc_position = pg.Vector2(pc.rect.center)
        pc_position += pg.Vector2(random.randint(-X_RANDOM, X_RANDOM), random.randint(-Y_RANDOM, 0))
        self.rect.center = pc_position
        super().attack()
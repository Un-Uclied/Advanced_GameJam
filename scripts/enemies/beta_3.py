import random

from scripts.entities import PlayerCharacter
from scripts.constants import *

from .base import GhostEnemy

hit_box_size = (110, 110)

x_random = 400
y_random = 400

class ThreeBeta(GhostEnemy):
    def __init__(self, spawn_position : pg.Vector2):
        rect = pg.Rect(spawn_position, hit_box_size)
        super().__init__("three_beta", rect,
                         max_health=150,
                         follow_speed=300, 
                         max_follow_range=700, 
                         attack_damage=25, 
                         max_attack_time=.8)

    def attack(self):
        pc = PlayerCharacter.singleton

        pc_position = pg.Vector2(pc.rect.center)
        pc_position += pg.Vector2(random.randint(-x_random, x_random), random.randint(-y_random, 0))
        self.rect.center = pc_position
        super().attack()
        
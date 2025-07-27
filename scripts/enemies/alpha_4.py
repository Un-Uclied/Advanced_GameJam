import json

from scripts.constants import *
from .base import WanderEnemy

ENEMY_NAME = "four_alpha"
with open("datas/enemy_data.json", 'r') as f:
    data = json.load(f)[ENEMY_NAME]
    HIT_BOX_SIZE = tuple(data["hit_box_size"])

    MOVE_SPEED_NORMAL = data["move_speed_normal"]
    MIN_CHANGE_TIMER_NORMAL = data["min_change_timer_normal"]
    MAX_CHANGE_TIMER_NORMAL = data["max_change_timer_normal"]

    MOVE_SPEED_CRAZY = data["move_speed_crazy"]
    MIN_CHANGE_TIMER_CRAZY = data["min_change_timer_crazy"]
    MAX_CHANGE_TIMER_CRAZY = data["max_change_timer_crazy"]

    CRAZY_RANGE = data["crazy_range"]

    FLIP_OFFSET = data["flip_offset"]
    
class FourAlpha(WanderEnemy):
    def __init__(self, spawn_position : pg.Vector2):
        super().__init__(
                         name=ENEMY_NAME,
                         rect=pg.Rect(spawn_position, HIT_BOX_SIZE),
                         min_change_timer=MIN_CHANGE_TIMER_NORMAL, 
                         max_change_timer=MAX_CHANGE_TIMER_NORMAL)

        self.flip_offset = {
            False: FLIP_OFFSET,
            True: FLIP_OFFSET
        }

    def update(self):
        ps = self.app.scene.player_status
        pc = ps.player_character

        entity_center = pg.Vector2(self.rect.center)
        player_center = pg.Vector2(pc.rect.center)
        current_distance = entity_center.distance_to(player_center)

        if current_distance < CRAZY_RANGE:
            self.ai.move_speed = MOVE_SPEED_CRAZY
            self.ai.min_change_timer = MIN_CHANGE_TIMER_CRAZY
            self.ai.max_change_timer = MAX_CHANGE_TIMER_CRAZY
        else:
            self.ai.move_speed = MOVE_SPEED_NORMAL
            self.ai.min_change_timer = MIN_CHANGE_TIMER_NORMAL
            self.ai.max_change_timer = MAX_CHANGE_TIMER_NORMAL

        super().update()
    
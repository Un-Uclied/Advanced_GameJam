

import pygame as pg
import random
import copy
import json

from .base.scene import Scene

from scripts.status import PlayerStatus
from scripts.entities import PlayerCharacter

from scripts.objects import GameObject
from scripts.ui import all_ui_types
from scripts.volume import *

from scripts.tilemap import Tilemap, spawn_all_entities

with open("datas/tilemap_data.json", 'r') as f:
    data = json.load(f)
    TILEMAP_FILES = data["tilemap_files"]
    TILEMAP_LEVEL_COUNT = data["tilemap_level_count"]

class MainGameScene(Scene):
    def on_scene_start(self):
        super().on_scene_start()
        
        self.player_status = PlayerStatus(self)

        self.level_count = 0
        self.current_difficulty = 0

        self.remaining_tilemap_files = copy.deepcopy(TILEMAP_FILES)

        self.tilemap = Tilemap()
        spawn_all_entities(self.tilemap)

        spawn_pos = pg.Vector2(self.tilemap.get_pos_by_data("spawners_entities", 0)[0])
        self.player_status.player_character = PlayerCharacter(spawn_pos)

        Sky()
        Clouds()
        Fog()
        
        # self.load_new_world()

    def update(self):
        self.player_status.on_update()
        super().update()

    def load_new_world(self):
        self.tilemap = Tilemap(random.choice(self.remaining_tilemap_files[str(self.current_difficulty)]))
        spawn_all_entities(self.tilemap)

        spawn_pos = pg.Vector2(self.tilemap.get_pos_by_data("spawners_entities", 0)[0])
        self.player_status.player_character = PlayerCharacter(spawn_pos)

        Sky()
        Clouds()
        Fog()
            
    def on_level_end(self):
        self.level_count += 1

        self.remaining_tilemap_files[str(self.current_difficulty)].remove(self.tilemap.file_name)

        if self.level_count >= TILEMAP_LEVEL_COUNT[str(self.current_difficulty)]:
            self.level_count = 0
            self.current_difficulty += 1

        GameObject.remove_all(do_not_destroy = all_ui_types)
        self.load_new_world()
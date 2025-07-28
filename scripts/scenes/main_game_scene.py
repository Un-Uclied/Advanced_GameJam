

import pygame as pg
import random
import copy
import json

from scripts.status import PlayerStatus
from scripts.entities import PlayerCharacter

from scripts.objects import GameObject
from scripts.ui import ALL_UI_TYPE
from scripts.volume import *

from scripts.tilemap import Tilemap, spawn_all_entities

with open("datas/tilemap_data.json", 'r') as f:
    data = json.load(f)
    TILEMAP_FILES = data["tilemap_files"]
    TILEMAP_LEVEL_COUNT = data["tilemap_level_count"]

from .base.scene import Scene
class MainGameScene(Scene):
    def on_scene_start(self):
        super().on_scene_start()
        
        # 씬 시작시 플레이어 스테이터스 한번만 만들고, 여기서 직접 관리.
        self.player_status = PlayerStatus(self)

        # 현재 레벨을 한 횟수
        self.level_count = 0
        # 현재 난이도
        self.current_difficulty = 0

        # 깊은복사 => 랜덤을 돌려서 가능한 레벨이 들어있음. (연속으로 같은 레벨을 하면 재미없기 때문에, 한번한 레벨은 여기에서 지움.)
        self.remaining_tilemap_files = copy.deepcopy(TILEMAP_FILES)

        self.load_new_level()

    def update(self):
        # !!!여기서 직접 관리!!!
        self.player_status.update()
        super().update()

    def load_new_level(self):
        # 가능한 타일맵 들중 난이도에 맞게 랜덤으로 선택
        self.tilemap = Tilemap(random.choice(self.remaining_tilemap_files[str(self.current_difficulty)]))
        # 플레이어는 제외하고 모든 엔티티 (적, 빛 포함) 생성
        spawn_all_entities(self.tilemap)

        # 플레이어는 따로
        spawn_pos = pg.Vector2(self.tilemap.get_pos_by_data("spawners_entities", 0)[0])
        #self.player_status에서 접근 가능하게 직접 여기서 연결 (조금 위험)
        self.player_status.player_character = PlayerCharacter(spawn_pos)

        Sky()
        Clouds()
        Fog()
            
    def on_level_end(self):
        self.level_count += 1

        # 이미 한거 지우기
        self.remaining_tilemap_files[str(self.current_difficulty)].remove(self.tilemap.file_name)

        #난이도 증가
        if self.level_count >= TILEMAP_LEVEL_COUNT[str(self.current_difficulty)]:
            self.level_count = 0
            self.current_difficulty += 1

        # UI빼고 모든 엔티티, 적, 빛, 플레이어, 타일맵, 파티클, 탄환 등등 다 지워버림.
        GameObject.remove_all(do_not_destroy = ALL_UI_TYPE)
        # 레벨 새로 만들기!!
        self.load_new_level()
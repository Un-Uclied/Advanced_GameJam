from .tilemap import Tilemap

from scripts.volume import Light
from scripts.entities import Soul, Portal
from scripts.enemies import *

SPAWNER_ENTITY_MAP = {
    1: lambda pos: Light(360, pos),
    2: lambda pos: Soul(pos),
    3: lambda pos: Portal(pos),
}

SPAWNER_ENEMY_MAP = {
    0 : lambda pos: OneAlpha  (pos),
    1 : lambda pos: OneBeta   (pos),
    2 : lambda pos: TwoAlpha  (pos),
    3 : lambda pos: TwoBeta   (pos),
    4 : lambda pos: ThreeAlpha(pos),
    5 : lambda pos: ThreeBeta (pos),
    6 : lambda pos: FourAlpha (pos),
    7 : lambda pos: FourBeta  (pos),
    8 : lambda pos: FiveOmega (pos)
}

def spawn_all_entities(tilemap: Tilemap):
        for spawner_id, constructor in SPAWNER_ENEMY_MAP.items():
            for pos in tilemap.get_pos_by_data("spawners_enemies", spawner_id):
                instance = constructor(pos)
        for spawner_id, constructor in SPAWNER_ENTITY_MAP.items():
            for pos in tilemap.get_pos_by_data("spawners_entities", spawner_id):
                if spawner_id == 0: #플레이어는 따로
                    continue
                instance = constructor(pos)
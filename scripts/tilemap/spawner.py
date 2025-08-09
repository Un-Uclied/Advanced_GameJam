from scripts.volume import Light
from scripts.entities import Soul, Portal
from scripts.enemies import *
from .tilemap import Tilemap

LIGHT_SIZE = 360

SPAWNER_ENTITY_MAP = {
    # 0: lambda pos: PlayerCharacter(pos),  # 플레이어는 씬에서 직접 생성
    1: lambda pos: Light(LIGHT_SIZE, pos),  # 빛 타일맵 위치에 맞게 생성
    2: lambda pos: Soul(pos),
    3: lambda pos: Portal(pos),
}

SPAWNER_ENEMY_MAP = {
    0: lambda pos: OneAlpha(pos),
    1: lambda pos: OneBeta(pos),
    2: lambda pos: TwoAlpha(pos),
    3: lambda pos: TwoBeta(pos),
    4: lambda pos: ThreeAlpha(pos),
    5: lambda pos: ThreeBeta(pos),
    6: lambda pos: FourAlpha(pos),
    7: lambda pos: FourBeta(pos),
    8: lambda pos: FiveOmega(pos),
}

def spawn_all_entities(tilemap: Tilemap):
    """타일맵에서 적과 엔티티 스폰 (플레이어 제외)"""
    # 적 먼저 생성 (그려지는 순서 문제 때문에)
    for spawner_id, constructor in SPAWNER_ENEMY_MAP.items():
        for pos in tilemap.get_pos_by_data("spawners_enemies", spawner_id):
            constructor(pos)

    # 그 다음 엔티티 생성
    for spawner_id, constructor in SPAWNER_ENTITY_MAP.items():
        if spawner_id == 0:
            continue  # 플레이어 스폰 스킵
        for pos in tilemap.get_pos_by_data("spawners_entities", spawner_id):
            constructor(pos)
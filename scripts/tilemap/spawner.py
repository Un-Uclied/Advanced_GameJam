from scripts.volume import Light
from scripts.entities import Soul, Portal

LIGHT_SIZE = 360

SPAWNER_ENTITY_MAP = {
    #0: lambda pos: PlayerCharacter(pos),  #플레이어 캐릭터는 씬에서 직접 생성
    1: lambda pos: Light(LIGHT_SIZE, pos), #빛은 엔티티가 아니지만 빛 타일맵 생성시 빛도 위치에 맞게 생성 해야함
    2: lambda pos: Soul(pos),
    3: lambda pos: Portal(pos),
}

from scripts.enemies import *
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

from .tilemap import Tilemap
def spawn_all_entities(tilemap: Tilemap):
        '''타일맵을 받으면 위치와 타입, 종류에 맞게 엔티티 및 적 생성 (플레이어는 제외)'''
        #적을 먼저 생성후, 다른 엔티티 생성 (생성한 순서에 따라 그려지는 순서가 달라져서 적을 미리 생성하면 플레이어나 영혼들 보다 앞에 있지 않게 함)
        for spawner_id, constructor in SPAWNER_ENEMY_MAP.items():
            for pos in tilemap.get_pos_by_data("spawners_enemies", spawner_id):
                constructor(pos)
                
        for spawner_id, constructor in SPAWNER_ENTITY_MAP.items():
            if spawner_id == 0: continue #플레이어는 스킵

            for pos in tilemap.get_pos_by_data("spawners_entities", spawner_id):
                constructor(pos)
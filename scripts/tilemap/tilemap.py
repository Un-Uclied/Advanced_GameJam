import pygame as pg
import json

from scripts.constants import *
from scripts.camera import *
from scripts.core import *

#예 : 오른쪽, 아래에 타일이 있다면 내(타일) 이미지를 0번으로 바꿔라
#예 : 4방향 전부 타일이 있다면 내 이미지를 8번으로 바꿔라
AUTOTILE_MAP = {
    tuple(sorted([(1, 0), (0, 1)])): 0,
    tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,
    tuple(sorted([(-1, 0), (0, 1)])): 2,
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 3,
    tuple(sorted([(-1, 0), (0, -1)])): 4,
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5,
    tuple(sorted([(1, 0), (0, -1)])): 6,
    tuple(sorted([(1, 0), (0, -1), (0, 1)])): 7,
    tuple(sorted([(1, 0), (-1, 0), (0, 1), (0, -1)])): 8,
}

NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]

AUTO_TILE_TILES = ["dirt"]
IN_GRID_TILES = ["dirt"]
DO_NOT_RENDER_TILES = ["spawners_entities", "spawners_enemies"]

# big ass number
CACHE_SURFACE_SIZE = pg.Vector2(15000, 15000)

BASE_TILEMAP_PATH = "data/tilemaps/"

class Tilemap(GameObject):
    '''
    타일맵 클래스!!! 엄청 중요함!! 엔티티 만들기전에 만들어짐

    :param file_name: 기본은 data/tilemaps/temp.json에 있는거 불러옴
    '''
    
    def __init__(self, file_name: str = "temp.json"):
        super().__init__()
        self.file_name = file_name

        with open(BASE_TILEMAP_PATH + self.file_name, 'r', encoding="utf-8") as f:
            json_data = json.load(f)

        self.tile_size = json_data["tile_size"]
        self.in_grid: dict[str, dict] = json_data["in_grid"]
        self.off_grid: list = json_data["off_grid"]

        self.cache = pg.Surface(CACHE_SURFACE_SIZE, pg.SRCALPHA)
        self.rerender()

    def get_pos_by_data(self, tile_type: str, variant: int = 0) -> list[pg.Vector2]:
        '''타일 타입이랑 인덱스 주면 그 타일들의 위치 반환 (그리드 안, 밖 전부)'''
        matched = []
        for tile in list(self.in_grid.values()) + self.off_grid:
            if tile["type"] == tile_type and tile.get("variant", 0) == variant:
                world_pos = pg.Vector2(tile["pos"][0] * self.tile_size, tile["pos"][1] * self.tile_size)
                matched.append(world_pos)
        return matched

    def tiles_around(self, pos: pg.Vector2):
        '''받은 위치 주변 타일 데이터를 반환 (주의 : 그리드 안에 있는것만)'''
        result = []
        tile_loc = (int(pos.x // self.tile_size), int(pos.y // self.tile_size))
        for offset in NEIGHBOR_OFFSETS:
            key = f"{tile_loc[0] + offset[0]},{tile_loc[1] + offset[1]}"
            if key in self.in_grid:
                result.append(self.in_grid[key])
        return result

    def physic_tiles_around(self, pos: pg.Vector2) -> list[pg.Rect]:
        '''받은 위치 주변의 충돌 가능한 타일을 찾아서 Rect를 반환'''
        rects = []
        for tile in self.tiles_around(pos):
            if tile.get("can_collide"):
                tile_pos = pg.Vector2(tile['pos']) * self.tile_size
                rects.append(pg.Rect(tile_pos, (self.tile_size, self.tile_size)))
        return rects

    def autotile(self):
        #그리드 안에 있는것만 검사
        for tile in self.in_grid.values():
            neighbors = set()
            #타일 각각 4방향 검사
            for shift in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
                check_pos = f"{tile['pos'][0] + shift[0]},{tile['pos'][1] + shift[1]}"
                if check_pos in self.in_grid and self.in_grid[check_pos]['type'] == tile['type']:
                    neighbors.add(shift)
            sorted_neighbors = tuple(sorted(neighbors))

            #오토타일 가능 한 타일 타입이고, AUTOTILE_MAP에 키가 있다면 AUTOTILE_MAP에 따라 이 타일의 인덱스 바꾸기
            if tile['type'] in AUTO_TILE_TILES and sorted_neighbors in AUTOTILE_MAP:
                tile['variant'] = AUTOTILE_MAP[sorted_neighbors]

    def rerender(self):
        # 순환 참조 피하기
        from scripts.scenes import TileMapEditScene
        self.cache.fill((0, 0, 0, 0)) # 캐시를 초기화합니다.

        for data in self.off_grid:
            if data["type"] in DO_NOT_RENDER_TILES and not isinstance(self.app.scene, TileMapEditScene):
                continue
            # 수정된 draw_tile 호출
            self.draw_tile(self.cache, data)

        for data in self.in_grid.values():
            if data["type"] in DO_NOT_RENDER_TILES and not isinstance(self.app.scene, TileMapEditScene):
                continue
            # 수정된 draw_tile 호출
            self.draw_tile(self.cache, data)

    def draw_tile(self, surface: pg.Surface, data: dict):
        tile_asset = self.app.ASSETS["tilemap"]
        world_pos = pg.Vector2(data["pos"]) * self.tile_size

        image = tile_asset[data["type"]][data["variant"]]
        
        # 캐시에 그릴 때 월드 좌표에 DRAW_OFFSET을 더하여 절대 위치에 렌더링
        cache_pos = world_pos + CACHE_SURFACE_SIZE / 2
        surface.blit(image, (round(cache_pos.x), round(cache_pos.y)))

    def draw(self):
        super().draw()

        surface = self.app.surfaces[LAYER_OBJ]
        camera = self.app.scene.camera
        
        # 캐시의 월드 시작점(-DRAW_OFFSET)을 화면 좌표로 변환
        cache_screen_pos = CameraMath.world_to_screen(camera, -CACHE_SURFACE_SIZE/2)
        surface.blit(self.cache, cache_screen_pos)

    def save_file(self, file_name: str = "temp.json"):
        '''현재 데이터 저장'''
        with open(BASE_TILEMAP_PATH + '/' + file_name, 'w', encoding="utf-8") as f:
            json.dump({
                "tile_size": self.tile_size,
                "in_grid": self.in_grid,
                "off_grid": self.off_grid
            }, f)
import pygame as pg
import json

from scripts.constants import *
from scripts.camera import *
from scripts.core import *

# --- 상수 및 맵 데이터 ---

# 자동 타일링에서 주변 타일 조합별로 해당 타일 이미지 인덱스를 매핑함
# 예: 오른쪽과 아래에 타일이 있으면 variant=0, 4방향 모두 타일 있으면 variant=8
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

# 검사할 주변 타일 좌표 오프셋 (현재 타일 중심 좌표 기준)
NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]

# 자동 타일링이 적용되는 타일 종류 리스트
AUTO_TILE_TILES = ["dirt", "stone", "dead_grass"]

# 그리드 내에 위치하는 타일 타입
IN_GRID_TILES = ["dirt", "stone", "dead_grass", "wood_struct"]

# 렌더링하지 않을 타일 타입 (스폰 지점 같은 것들)
DO_NOT_RENDER_TILES = ["spawners_entities", "spawners_enemies"]

# 엄청 큰 크기의 캐시용 서피스 크기 (월드 좌표를 모두 커버)
CACHE_SURFACE_SIZE = pg.Vector2(15000, 15000)

# 타일맵 데이터 기본 경로
BASE_TILEMAP_PATH = "data/tilemaps/"


class Tilemap(GameObject):
    """
    타일맵 클래스 (게임 월드 타일 데이터 및 렌더링 담당)

    특징:
    - JSON 파일에서 타일 데이터(그리드 안팎)를 불러와 관리
    - 오토타일링 적용 가능 (주변 타일 상황에 따라 타일 이미지 variant 결정)
    - 캐시 서피스에 한 번 그린 후 매 프레임 캐시를 렌더링하여 성능 최적화
    - 충돌 가능 타일 정보 제공
    - 그리드 내부 및 외부 타일 구분 및 접근 가능

    주의점:
    - CACHE_SURFACE_SIZE가 너무 작으면 월드 좌표 전부 커버 안 될 수 있음 (충분히 크게 설정할 것)
    - 현재는 가로, 세로 방향 타일 크기가 같아야 함
    - 'off_grid' 타일은 월드 어디든 위치할 수 있음
    """

    def __init__(self, file_name: str = "temp.json"):
        super().__init__()
        self.file_name = file_name

        # JSON 데이터 불러오기
        with open(BASE_TILEMAP_PATH + self.file_name, 'r', encoding="utf-8") as f:
            json_data = json.load(f)

        self.tile_size = json_data["tile_size"]
        self.in_grid: dict[str, dict] = json_data["in_grid"]
        self.off_grid: list = json_data["off_grid"]

        # 오토타일 및 렌더링용 큰 캐시 서피스 생성 (투명도 지원)
        self.cache = pg.Surface(CACHE_SURFACE_SIZE, pg.SRCALPHA)
        self.rerender()  # 캐시에 초기 타일 데이터 렌더링

    def get_pos_by_data(self, tile_type: str, variant: int = 0) -> list[pg.Vector2]:
        """
        해당 타입과 variant를 가진 타일 위치 리스트 반환

        :param tile_type: 타일 종류 (예: "dirt")
        :param variant: variant 인덱스
        :return: 월드 좌표 리스트 (pg.Vector2)
        """
        matched = []
        for tile in list(self.in_grid.values()) + self.off_grid:
            if tile["type"] == tile_type and tile.get("variant", 0) == variant:
                # 그리드 좌표를 월드 좌표로 변환
                world_pos = pg.Vector2(tile["pos"][0] * self.tile_size, tile["pos"][1] * self.tile_size)
                matched.append(world_pos)
        return matched

    def tiles_around(self, pos: pg.Vector2) -> list[dict]:
        """
        주어진 월드 좌표 주변 타일 정보 반환 (그리드 내 타일만)

        :param pos: 월드 좌표
        :return: 타일 dict 리스트
        """
        result = []
        tile_loc = (int(pos.x // self.tile_size), int(pos.y // self.tile_size))
        for offset in NEIGHBOR_OFFSETS:
            key = f"{tile_loc[0] + offset[0]},{tile_loc[1] + offset[1]}"
            if key in self.in_grid:
                result.append(self.in_grid[key])
        return result

    def physic_tiles_around(self, pos: pg.Vector2) -> list[pg.Rect]:
        """
        충돌 가능 타일 주변 목록을 Rect로 반환 (충돌 검사용)

        :param pos: 월드 좌표
        :return: 충돌 타일들의 pg.Rect 리스트
        """
        rects = []
        for tile in self.tiles_around(pos):
            if tile.get("can_collide"):
                tile_pos = pg.Vector2(tile['pos']) * self.tile_size
                rects.append(pg.Rect(tile_pos, (self.tile_size, self.tile_size)))
        return rects

    def autotile(self):
        """
        오토타일링 알고리즘 적용

        각 그리드 내부 타일마다 4방향 이웃 타일 검사 후,
        주변 타일 조합에 따라 variant 값을 AUTOTILE_MAP에 맞춰 자동 설정함.

        예:
            - 만약 오른쪽과 아래 타일이 있다면 variant=0
            - 4방향 모두 타일이 있다면 variant=8
        """
        for tile in self.in_grid.values():
            neighbors = set()
            # 4방향 검사 (우, 좌, 상, 하)
            for shift in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
                check_pos = f"{tile['pos'][0] + shift[0]},{tile['pos'][1] + shift[1]}"
                if check_pos in self.in_grid and self.in_grid[check_pos]['type'] == tile['type']:
                    neighbors.add(shift)
            sorted_neighbors = tuple(sorted(neighbors))

            # 조건 만족 시 variant 변경
            if tile['type'] in AUTO_TILE_TILES and sorted_neighbors in AUTOTILE_MAP:
                tile['variant'] = AUTOTILE_MAP[sorted_neighbors]

    def rerender(self):
        """
        캐시 서피스에 타일 전체를 다시 그림

        - off_grid 타일과 in_grid 타일 모두 그림
        - 엄청 무거움!!! 매프레임마다 부르면 fps30가는거 순식간;;
        - 특정 씬(예: 타일맵 에디터)에서만 렌더링 제외 타일을 표시
        """
        from scripts.scenes import TileMapEditScene  # 순환 참조 방지용 임포트

        self.cache.fill((0, 0, 0, 0))  # 투명으로 초기화

        for data in self.off_grid:
            # 렌더링 제외 타일 필터링
            if data["type"] in DO_NOT_RENDER_TILES and not isinstance(self.app.scene, TileMapEditScene):
                continue
            self.draw_tile(self.cache, data)

        for data in self.in_grid.values():
            if data["type"] in DO_NOT_RENDER_TILES and not isinstance(self.app.scene, TileMapEditScene):
                continue
            self.draw_tile(self.cache, data)

    def draw_tile(self, surface: pg.Surface, data: dict):
        """
        주어진 타일 데이터를 주어진 서피스에 그림

        :param surface: 타일을 그릴 서피스 (주로 캐시 서피스)
        :param data: 타일 데이터 dict (pos, type, variant 등)
        """
        tile_asset = self.app.ASSETS["tilemap"]
        world_pos = pg.Vector2(data["pos"]) * self.tile_size

        image = tile_asset[data["type"]][data["variant"]]

        # 캐시에 그릴 때 월드 좌표 + 캐시 오프셋 (월드 좌표 중심을 캐시 중앙으로 이동)
        cache_pos = world_pos + CACHE_SURFACE_SIZE / 2
        surface.blit(image, (round(cache_pos.x), round(cache_pos.y)))

    def draw(self):
        """
        매 프레임 호출되는 그리기 함수.

        캐시 서피스를 화면에 그리며, 카메라 이동 효과를 적용.
        """
        super().draw()

        surface = self.app.surfaces[LAYER_OBJ]
        camera = self.app.scene.camera

        # 캐시 서피스의 월드 시작점 (-오프셋)을 스크린 좌표로 변환
        cache_screen_pos = CameraMath.world_to_screen(camera, -CACHE_SURFACE_SIZE / 2)
        surface.blit(self.cache, cache_screen_pos)

    def save_file(self, file_name: str = "temp.json"):
        """
        현재 타일맵 데이터를 JSON 파일로 저장

        :param file_name: 저장할 파일 이름 (기본 temp.json)
        """
        with open(BASE_TILEMAP_PATH + '/' + file_name, 'w', encoding="utf-8") as f:
            json.dump({
                "tile_size": self.tile_size,
                "in_grid": self.in_grid,
                "off_grid": self.off_grid
            }, f)
import pygame as pg
import json

from scripts.constants import *
from scripts.camera import *
from scripts.utils import *

# 타일맵 데이터 기본 경로
BASE_TILEMAP_PATH = "data/tilemaps/"

class TilemapData:
    def __init__(self, file_name : str = "temp.json"):
        self.file_name = file_name

        # JSON 데이터 불러오기
        with open(BASE_TILEMAP_PATH + self.file_name, 'r', encoding="utf-8") as f:
            json_data = json.load(f)

        self.tile_size : int             = json_data["tile_size"]
        self.in_grid   : dict[str, dict] = json_data["in_grid"]
        self.off_grid  : list            = json_data["off_grid"]

    def get_positions_by_types(self, tile_type: str, variant: int = 0) -> list[pg.Vector2]:
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
        
        # 검사할 주변 타일 좌표 오프셋 (현재 타일 중심 좌표 기준)
        NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]

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

class TilemapRenderer(GameObject):
    def __init__(self, tilemap_data : TilemapData,
                 cache_surface_size : pg.Vector2 = pg.Vector2(15000, 15000),
                 do_not_render_tiles : list[str] = ["spawners_entities", "spawners_enemies", "custom_point"]):
        super().__init__()

        self.data = tilemap_data
        self.cache_surface_size = cache_surface_size
        self.do_not_render_tiles = do_not_render_tiles

        self.cache_surface = pg.Surface(cache_surface_size, pg.SRCALPHA)
        self.rerender()

    def rerender(self):
        """
        캐시 서피스에 타일 전체를 다시 그림

        - off_grid 타일과 in_grid 타일 모두 그림
        - 엄청 무거움!!! 매프레임마다 부르면 fps30가는거 순식간;;
        - 특정 씬(예: 타일맵 에디터)에서만 렌더링 제외 타일을 표시
        """
        from scripts.scenes import TileMapEditScene  # 순환 참조 방지용 임포트

        self.cache_surface.fill((0, 0, 0, 0))  # 투명으로 초기화

        for data in self.data.off_grid:
            # 렌더링 제외 타일 필터링
            if data["type"] in self.do_not_render_tiles and not isinstance(self.scene, TileMapEditScene):
                continue
            self.draw_tile(self.cache_surface, data)

        for data in self.data.in_grid.values():
            if data["type"] in self.do_not_render_tiles and not isinstance(self.scene, TileMapEditScene):
                continue
            self.draw_tile(self.cache_surface, data)

    def draw_tile(self, surface: pg.Surface, data: dict):
        """
        주어진 타일 데이터를 주어진 서피스에 그림

        :param surface: 타일을 그릴 서피스 (주로 캐시 서피스)
        :param data: 타일 데이터 dict (pos, type, variant 등)
        """
        tile_asset = self.app.ASSETS["tilemap"]
        world_pos = pg.Vector2(data["pos"]) * self.data.tile_size

        image = tile_asset[data["type"]][data["variant"]]

        # 캐시에 그릴 때 월드 좌표 + 캐시 오프셋 (월드 좌표 중심을 캐시 중앙으로 이동)
        cache_pos = world_pos + self.cache_surface_size / 2
        surface.blit(image, (round(cache_pos.x), round(cache_pos.y)))

    def draw(self):
        """
        매 프레임 호출되는 그리기 함수.

        캐시 서피스를 화면에 그리며, 카메라 이동 효과를 적용.
        """
        super().draw()

        surface = self.app.surfaces[LAYER_OBJ]
        camera = self.scene.camera

        # 캐시 서피스의 월드 시작점 (-오프셋)을 스크린 좌표로 변환
        cache_screen_pos = CameraMath.world_to_screen(camera, -self.cache_surface_size / 2)
        surface.blit(self.cache_surface, cache_screen_pos)
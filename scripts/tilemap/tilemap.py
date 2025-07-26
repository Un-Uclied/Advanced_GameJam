import pygame as pg
import json

from scripts.constants import *
from scripts.objects import GameObject

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

BASE_TILEMAP_PATH = "datas/tilemaps/"

class Tilemap(GameObject):
    def __init__(self, json_file_name : str = "temp.json"):
        super().__init__()
        self.json_file_name = json_file_name
        
        file = open(BASE_TILEMAP_PATH + self.json_file_name, 'r')
        json_data = json.load(file)
        file.close()

        self.tile_size : int = json_data["tile_size"]
        self.in_grid = json_data["in_grid"]
        self.off_grid = json_data["off_grid"]

    def get_pos_by_data(self, tile_type: str, variant: int = 0) -> list[pg.Vector2]:
        matched_positions = []

        for tile in self.in_grid.values():
            if tile["type"] == tile_type and tile.get("variant", 0) == variant:
                world_pos = pg.Vector2(tile["pos"][0] * self.tile_size, tile["pos"][1] * self.tile_size)
                matched_positions.append(world_pos)

        for tile in self.off_grid:
            if tile["type"] == tile_type and tile.get("variant", 0) == variant:
                world_pos = pg.Vector2(tile["pos"][0] * self.tile_size, tile["pos"][1] * self.tile_size)
                matched_positions.append(world_pos)

        return matched_positions
    
    def tiles_around(self, pos : pg.Vector2):
        around_in_grid = []
        tile_loc = (int(pos.x // self.tile_size), int(pos.y // self.tile_size))
        for offset in NEIGHBOR_OFFSETS:
            current_check_location = f"{int(tile_loc[0] + offset[0])},{int(tile_loc[1] + offset[1])}"
            if current_check_location in self.in_grid:
                around_in_grid.append(self.in_grid[current_check_location])
        return around_in_grid
    
    def physic_tiles_around(self, pos : pg.Vector2) -> list[pg.Rect]:
        rects = []
        for tile in self.tiles_around(pg.Vector2(int(pos.x), int(pos.y))):
            if tile["can_collide"]:
                rects.append(pg.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))
        return rects
    
    def autotile(self):
        for loc in self.in_grid:
            tile = self.in_grid[loc]
            neighbors = set()
            for shift in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
                check_loc = f"{tile['pos'][0]+shift[0]},{tile['pos'][1] + shift[1]}"
                if check_loc in self.in_grid:
                    if self.in_grid[check_loc]['type'] == tile['type']:
                        neighbors.add(shift)
            neighbors = tuple(sorted(neighbors))
            if (tile['type'] in AUTO_TILE_TILES) and (neighbors in AUTOTILE_MAP):
                tile['variant'] = AUTOTILE_MAP[neighbors]

    def on_draw(self):
        screen = self.app.surfaces[LAYER_OBJ]
        camera = self.app.scene.camera
        tile_asset = self.app.ASSETS["tilemap"]

        from scripts.scenes import TileMapEditScene

        for data in self.off_grid:
            if data["type"] in DO_NOT_RENDER_TILES and not isinstance(self.app.scene, TileMapEditScene): continue
            world_pos = pg.Vector2(data["pos"][0] * self.tile_size, data["pos"][1] * self.tile_size)
            screen_pos = camera.world_to_screen(world_pos)
            image = tile_asset[data["type"]][data["variant"]]
            scaled_image = camera.get_scaled_surface(image)
            screen.blit(scaled_image, screen_pos)
        
        for data in self.in_grid.values():
            if data["type"] in DO_NOT_RENDER_TILES and not isinstance(self.app.scene, TileMapEditScene): continue
            world_pos = pg.Vector2(data["pos"][0] * self.tile_size, data["pos"][1] * self.tile_size)
            image = tile_asset[data["type"]][data["variant"]]
            scaled_image = camera.get_scaled_surface(image)
            screen.blit(scaled_image, camera.world_to_screen(world_pos))

    def save_file(self, json_file_name : str = "temp.json"):
        file = open(BASE_TILEMAP_PATH + '/' + json_file_name, 'w')
        json.dump({
            'tile_size' : self.tile_size,
            'in_grid' : self.in_grid, 
            'off_grid' : self.off_grid}, file)
        file.close()
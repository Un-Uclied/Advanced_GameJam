import pygame as pg
import json

from .game_objects import *
from datas.const import *

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
AUTOTILE_TYPES = {"grass", "stone"}

NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]

class Tilemap(GameObject):
    def __init__(self, json_file_name : str = "temp.json"):
        super().__init__()
        file = open(BASE_TILEMAP_PATH + '/' + json_file_name, 'r')
        json_data = json.load(file)
        file.close()

        self.tile_size : int = json_data["tile_size"]
        self._tiles = json_data["tiles"]
        self._objects = json_data["objects"]
        self._spawn_points = json_data["spawn_points"]

    def tiles_around(self, pos : pg.Vector2):
        around_tiles = []
        tile_loc = (int(pos.x // self.tile_size), int(pos.y // self.tile_size))
        for offset in NEIGHBOR_OFFSETS:
            current_check_location = f"{int(tile_loc[0] + offset[0])},{int(tile_loc[1] + offset[1])}"
            if current_check_location in self._tiles:
                around_tiles.append(self._tiles[current_check_location])
        return around_tiles
    
    def physic_tiles_around(self, pos : pg.Vector2) -> list[pg.Rect]:
        rects = []
        for tile in self.tiles_around(pg.Vector2(int(pos.x), int(pos.y))):
            if tile["can_collide"]:
                rects.append(pg.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))
        return rects
    
    def on_draw(self):
        super().on_draw()
        
        from .app import App #순환 참조 무서웡...

        camera = GameObject.current_scene.camera
        screen = App.singleton.screen
        tile_asset = App.singleton.ASSET_TILEMAP

        for obj_data in self._objects.copy():
            world_pos = pg.Vector2(obj_data["pos"][0] * self.tile_size, obj_data["pos"][1] * self.tile_size)
            screen_pos = camera.world_to_screen(world_pos)

            original_image = tile_asset[obj_data["type"]][obj_data["variant"]]
        
            screen.blit(camera.get_scaled_surface(original_image), screen_pos)
        
        for key in self._tiles.keys():
            tile_data = self._tiles[key]

            world_pos = pg.Vector2(tile_data["pos"][0] * self.tile_size, tile_data["pos"][1] * self.tile_size)
            screen_pos = camera.world_to_screen(world_pos)

            scaled_tile_size = int(self.tile_size * camera.scale)
            original_image = tile_asset[tile_data["type"]][tile_data["variant"]]
            scaled_image = pg.transform.scale(original_image, (scaled_tile_size, scaled_tile_size))

            App.singleton.screen.blit(scaled_image, screen_pos)
        
    def autotile(self):
        for loc in self._tiles:
            tile = self._tiles[loc]
            neighbors = set()
            for shift in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
                check_loc = f"{tile['pos'][0]+shift[0]},{tile['pos'][1] + shift[1]}"
                if check_loc in self._tiles:
                    if self._tiles[check_loc]['type'] == tile['type']:
                        neighbors.add(shift)
            neighbors = tuple(sorted(neighbors))
            if (tile['type'] in AUTOTILE_TYPES) and (neighbors in AUTOTILE_MAP):
                tile['variant'] = AUTOTILE_MAP[neighbors]

    def save_file(self, json_file_name : str = "temp.json"):
        file = open(BASE_TILEMAP_PATH + '/' + json_file_name, 'w')
        json.dump({
            'tile_size' : self.tile_size,
            'tiles' : self._tiles, 
            'objects' : self._objects,
            "spawn_points" :self._spawn_points}, file)
        file.close()
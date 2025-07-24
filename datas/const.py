import pygame as pg

SCREEN_SIZE = pg.Vector2(1480, 920)
TARGET_FPS = 60
SCREEN_FLAGS = pg.DOUBLEBUF | pg.HWSURFACE 
GAME_NAME = "GAME NAME"

ASSET_SCALE_BY = 2

BASE_IMAGE_PATH = "assets/images/"
BASE_TILEMAP_PATH = "datas/tilemaps/"

DEFAULT_FONT_NAME = "PF스타더스트 3.0 Bold.ttf"
BASE_FONT_PATH = "assets/fonts/"

LAYER_BG = "background"
LAYER_OBJ = "objects"
LAYER_ENTITY = "entities"
LAYER_DYNAMIC = "dynamics"
LAYER_VOLUME = "volume"
LAYER_INTERFACE = "interface"

AUTO_TILE_TILES = ["dirt"]
IN_GRID_TILES = ["dirt"]
OFF_GRID_TILES = ["props", "folliage", "statues"]
DO_NOT_RENDER_TILES = ["spawners"]

from scripts.entities import Player, Light2D, Soul, Portal, ThreeBeta, FourAlpha

SPAWNER_ENTITY_MAP = {
    0: lambda pos: Player(pg.Rect(pos.x, pos.y, 48, 128)),

    1: lambda pos: Light2D(360, pos),

    2: lambda pos: Soul(pg.Rect(pos.x, pos.y, 40, 80)),

    3: lambda pos: Portal(pg.Rect(pos.x, pos.y, 180, 180)),

    4: lambda pos: ThreeBeta(pg.Rect(pos.x, pos.y, 120, 120)),
    5: lambda pos: FourAlpha(pg.Rect(pos.x, pos.y, 80, 165)),
}
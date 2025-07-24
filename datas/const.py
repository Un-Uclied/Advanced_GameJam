import pygame as pg

SCREEN_SIZE = pg.Vector2(1200, 800)
TARGET_FPS = 60
SCREEN_FLAGS = pg.SCALED | pg.DOUBLEBUF | pg.HWSURFACE | pg.FULLSCREEN
GAME_NAME = "GAME NAME"

ASSET_SCALE_BY = 2

BASE_IMAGE_PATH = "assets/images/"
BASE_TILEMAP_PATH = "datas/tilemaps/"

DEFAULT_FONT_NAME = "PF스타더스트 3.0 Bold.ttf"
BASE_FONT_PATH = "assets/fonts/"
BASE_SOUND_PATH = "assets/sounds/"

LAYER_BG = "background"
LAYER_OBJ = "objects"
LAYER_ENTITY = "entities"
LAYER_DYNAMIC = "dynamics"
LAYER_VOLUME = "volume"
LAYER_INTERFACE = "interface"

AUTO_TILE_TILES = ["dirt"]
IN_GRID_TILES = ["dirt"]
OFF_GRID_TILES = ["props", "folliage", "statues"]
DO_NOT_RENDER_TILES = ["spawners", "enemy_spawners"]

ATTACK_DMGS = {
    "one_alpha" : 5,
    "one_beta" : 10,
    "two_alpha" : 10,
    "two_beta" : 15,
    "three_alpha" : 15,
    "three_beta" : 20,
    "four_alpha" : 25,
    "four_beta" : 25,
    "five_omega" : 30,
}

from scripts.entities import Light2D, Soul, Portal
SPAWNER_ENTITY_MAP = {
    1: lambda pos: Light2D(360, pos),
    2: lambda pos: Soul(pg.Rect(pos.x, pos.y, 40, 80)),
    3: lambda pos: Portal(pg.Rect(pos.x, pos.y, 180, 180)),
}

from scripts.enemies import OneAlpha, OneBeta, TwoAlpha, TwoBeta, ThreeAlpha, ThreeBeta, FourAlpha, FourBeta, FiveOmega
SPAWNER_ENEMY_MAP = {
    0 : lambda pos: OneAlpha  (pg.Rect(pos.x, pos.y, 120, 120)),
    1 : lambda pos: OneBeta   (pg.Rect(pos.x, pos.y, 120, 120)),
    2 : lambda pos: TwoAlpha  (pg.Rect(pos.x, pos.y, 120, 120)),
    3 : lambda pos: TwoBeta   (pg.Rect(pos.x, pos.y, 120, 120)),
    4 : lambda pos: ThreeAlpha(pg.Rect(pos.x, pos.y, 120, 120)),
    5 : lambda pos: ThreeBeta (pg.Rect(pos.x, pos.y, 120, 120)),
    6 : lambda pos: FourAlpha (pg.Rect(pos.x, pos.y, 80, 165)),
    7 : lambda pos: FourBeta  (pg.Rect(pos.x, pos.y, 80, 165)),
    8 : lambda pos: FiveOmega (pg.Rect(pos.x, pos.y, 80, 165))
}
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

ONE_ALPHA = "one_alpha"
ONE_BETA = "one_beta"
TWO_ALPHA = "two_alpha"
TWO_BETA = "two_beta"
THREE_ALPHA = "three_alpha"
THREE_BETA = "three_beta"
FOUR_ALPHA = "four_alpha"
FOUR_BETA = "four_beta"
FIVE_OMEGA = "five_omega"

from scripts.volume import Light
from scripts.entities import Soul, Portal
SPAWNER_ENTITY_MAP = {
    1: lambda pos: Light(360, pos),
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
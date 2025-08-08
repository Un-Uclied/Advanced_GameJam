import pygame as pg

from scripts.constants import *
from scripts.ui import *
from scripts.core import *
from .base import Scene

class OpeningScene(Scene):
    def on_scene_start(self):
        CutScene("opening", self.cut_scene_end)
        super().on_scene_start()

    def cut_scene_end(self):
        # 이 오프닝 컷씬은 게임을 처음틀었을때만 보여주고 나중에 다시 틀때엔 안 보여줌.
        self.app.player_data["is_first_start"] = False
        self.app.change_scene("main_menu_scene")

    def draw(self):
        # 배경을 검정색으로 칠하기
        surface = self.app.surfaces[LAYER_INTERFACE]
        pg.draw.rect(surface, "black", surface.get_frect())
        super().draw()
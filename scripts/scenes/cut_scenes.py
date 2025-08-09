import pygame as pg
from scripts.constants import *
from scripts.core import *
from scripts.ui import *
from .base import Scene

class CutSceneBase(Scene):
    def __init__(self, cutscene_name, next_chapter, next_level, first_start_flag=None):
        super().__init__()
        self.cutscene_name = cutscene_name
        self.next_chapter = next_chapter
        self.next_level = next_level
        self.first_start_flag = first_start_flag  # 첫 시작 여부 조절용 옵션

    def on_scene_start(self):
        CutScene(self.cutscene_name, self.cut_scene_end)
        super().on_scene_start()

    def cut_scene_end(self):
        if self.first_start_flag is not None:
            self.app.player_data[self.first_start_flag] = False
        if self.next_chapter is not None and self.next_level is not None:
            self.app.registered_scenes["main_game_scene"].current_chapter = self.next_chapter
            self.app.registered_scenes["main_game_scene"].current_level = self.next_level
            self.app.change_scene("main_game_scene")
        else:
            # 예: 오프닝 씬 같은 경우 다음 씬 직접 지정
            self.app.change_scene("main_menu_scene")

    def draw(self):
        surface = self.app.surfaces[LAYER_INTERFACE]
        pg.draw.rect(surface, "black", surface.get_rect())
        super().draw()

class OpeningScene(CutSceneBase):
    def __init__(self):
        super().__init__("opening", None, None, first_start_flag="is_first_start")

class Tutorial1Scene(CutSceneBase):
    def __init__(self):
        super().__init__("tutorial_1", 1, 0)

class Tutorial2Scene(CutSceneBase):
    def __init__(self):
        super().__init__("tutorial_2", 1, 1)

class NoLightCutScene(CutSceneBase):
    def __init__(self):
        super().__init__("no_lights", 3, 4)

class NoSoulsCutScene(CutSceneBase):
    def __init__(self):
        super().__init__("no_souls", 2, 2)

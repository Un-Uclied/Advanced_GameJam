import pygame as pg

from scripts.volume import Sky
from scripts.ui import ImageButton

from .base.scene import Scene
class MainMenuScene(Scene):
    def on_scene_start(self):
        super().on_scene_start()
        Sky()

        #이렇게 생성자에서 로컬 함수 만들고 모든 버튼에 넣기
        def callback(name : str, button : ImageButton):
            if name == "temp":
                self.app.change_scene("main_game_scene")

        ImageButton("temp", pg.Vector2(400, 400), callback)
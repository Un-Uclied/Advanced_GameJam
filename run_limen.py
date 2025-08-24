'''pip install pygame-ce'''

RUN_EDITOR = "editor_scene"
RUN_GAME = "main_menu_scene"

target_scene = RUN_GAME

from scripts.app import App
App(target_scene).run()
'''pip install pygame-ce'''

from scripts.app import App
app = App('main_menu_scene')
app.sound_manager.play_bgm("main_menu")
app.run() 
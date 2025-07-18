import pygame as pg
import pygame.freetype

from datas.const import *
from .values import *
from .game_objects import GameObject

class TextRenderer(GameObject):
    def __init__(self, text_value : StringValue | str, 
                 position : pg.Vector2,
                 font_size: int = 24,
                 color: pg.Color = pg.Color(255, 255, 255),
                 use_camera : bool =  True,
                 font_name : str | None =  None):
        
        super().__init__()
        self.txt = text_value
        self._pos = position
        self._color = color
        self._use_camera = use_camera
    
        if font_name is None:
            self._font = pygame.freetype.Font(f"{BASE_FONT_PATH}/{DEFAULT_FONT_NAME}", font_size)
        else:
            self._font = pygame.freetype.Font(f"{BASE_FONT_PATH}/{font_name}", font_size)

    def set_font_size(self, value):
        self._font.size = value

    def on_draw(self):
        if self._use_camera:
            pos = GameObject.current_scene.camera.world_to_screen(self._pos)
        else:
            pos = self._pos

        from .app import App
        screen = App.singleton.screen
        if isinstance(self.txt, StringValue) == False or hasattr(self.txt, "value") == False:
            #일반 문자열
            self._font.render_to(screen, pos, self.txt, self._color)
        else:
            #문자열 Value일때
            self._font.render_to(screen, pos, self.txt.value, self._color)
import pygame as pg

from datas.const import *
from .values import *
from .objects import *

class TextRenderer(UserInterface):
    def __init__(self, 
                 text_value: StringValue | str, 
                 position: pg.Vector2,
                 font_size: int = 24,
                 color: pg.Color = pg.Color(255, 255, 255),
                 use_camera: bool = True):
        
        super().__init__(use_camera)
        self.txt = text_value
        self._pos = position
        self._color = color
        self._font_size = font_size
        self._font = pg.font.Font(f"{BASE_FONT_PATH}/{DEFAULT_FONT_NAME}", self._font_size)

    def set_font_size(self, value):
        self._font_size = value
        self._font = pg.font.Font(f"{BASE_FONT_PATH}/{DEFAULT_FONT_NAME}", self._font_size)

    def on_update(self):
        pass

    def on_draw(self):
        if self.use_camera:
            pos = self.app.scene.camera.world_to_screen(self._pos)
        else:
            pos = self._pos

        # 텍스트 렌더링 (Surface 생성)
        text = self.txt.value if isinstance(self.txt, StringValue) else self.txt
        text_surf = self._font.render(text, True, self._color)
        self.app.screen.blit(text_surf, pos)
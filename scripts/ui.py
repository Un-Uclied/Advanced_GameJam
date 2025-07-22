import pygame as pg

from datas.const import *
from .values import *
from .objects import *

class TextRenderer(UserInterface):
    def __init__(self, 
                 text_value: StringValue | str, 
                 position: pg.Vector2,
                 font_name : str = "default",
                 font_size: int = 24,
                 color: pg.Color = pg.Color(255, 255, 255),
                 use_camera: bool = False):
        
        super().__init__(use_camera)
        self.txt = text_value
        self.pos = position
        self.color = color
        self.font = pg.font.Font(self.app.ASSET_FONT_PATHS[font_name], font_size)

    def on_update(self):
        pass

    def on_draw(self):
        if self.use_camera:
            pos = self.app.scene.camera.world_to_screen(self.pos)
        else:
            pos = self.pos

        text = self.txt.value if isinstance(self.txt, StringValue) else self.txt
        text_surf = self.font.render(text, False, self.color)
        text_surf = self.app.scene.camera.get_scaled_surface(text_surf) if self.use_camera else text_surf

        screen = self.app.surfaces[LAYER_INTERFACE]
        screen.blit(text_surf, pos)
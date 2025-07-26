from scripts.constants import *
from scripts.objects import GameObject

class Sky(GameObject):
    def __init__(self, sky_name : str = "default"):
        super().__init__()
        self.surfaces = self.app.ASSETS["backgrounds"]["sky"][sky_name]

    def on_draw(self):
        super().on_draw()
        for surface in self.surfaces:
            self.app.surfaces[LAYER_BG].blit(surface, (0, 0))
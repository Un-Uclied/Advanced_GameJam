from scripts.constants import *
from scripts.objects import GameObject

class Sky(GameObject):
    def __init__(self, asset_key : str = "default"):
        super().__init__()
        self.asset_key = asset_key

    def on_draw(self):
        super().on_draw()
        self.app.surfaces[LAYER_BG].blit(self.app.ASSETS["backgrounds"][self.asset_key], (0, 0))
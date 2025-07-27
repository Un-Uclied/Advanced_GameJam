from scripts.constants import *
from scripts.objects import *

class Sky(GameObject):
    def __init__(self, sky_name : str = "default"):
        super().__init__()

        #App클래스의 에셋의 ["backgrounds"]["sky"][하늘 이름]은 list[pg.Surface]
        self.surfaces = self.app.ASSETS["backgrounds"]["sky"][sky_name]

    def draw(self):
        super().draw()
        for surface in self.surfaces:
            self.app.surfaces[LAYER_BG].blit(surface, (0, 0))
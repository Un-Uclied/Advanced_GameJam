from scripts.constants import *
from scripts.core import *

class Sky(GameObject):
    '''
    그냥 Sky()하면 바로 하늘 생김 (구름 & 안개 제외)

    :param sky_name: 하늘 에셋 키인데 그냥 보스전 같은데 빼고 그냥 "default"로 써라 ㅇㅇ
    '''

    def __init__(self, sky_name : str = "default"):
        super().__init__()

        #App클래스의 에셋의 ["backgrounds"]["sky"][하늘 이름]은 list[pg.Surface]
        self.surfaces = self.app.ASSETS["backgrounds"]["sky"][sky_name]
        self.cache = pg.Surface(self.surfaces[0].get_size())
        for surface in self.surfaces:
            self.cache.blit(surface, (0, 0))

    def draw(self):
        super().draw()
        self.app.surfaces[LAYER_BG].blit(self.cache, (0, 0))
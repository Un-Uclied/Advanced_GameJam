from scripts.constants import *
from scripts.camera import *
from scripts.core import *

class LineWarning(GameObject):
    def __init__(self, start : pg.Vector2, end : pg.Vector2, thickness : int, warn_color : pg.Color = pg.Color("red")):
        super().__init__()
        self.start = start
        self.end = end
        self.thickness = thickness
        self.warn_color = warn_color
    
    def draw(self):
        super().draw()

        # 월드좌표 → 화면좌표 변환
        draw_start = CameraMath.world_to_screen(self.app.scene.camera, self.start)
        draw_end = CameraMath.world_to_screen(self.app.scene.camera, self.end)

        # 방향벡터
        dir_vec = pg.Vector2(draw_end) - pg.Vector2(draw_start)
        if dir_vec.length_squared() == 0:
            return  # 방향 없으면 그리지 않음

        dir_vec.normalize_ip()

        # 양쪽으로 확장
        p1 = draw_start - dir_vec * 3000
        p2 = draw_start + dir_vec * 3000

        # 직선 그리기
        pg.draw.line(
            self.app.surfaces[LAYER_INTERFACE],
            self.warn_color,
            p1, p2,
            self.thickness
        )

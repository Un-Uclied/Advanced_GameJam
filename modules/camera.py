import pygame as pg

class Camera:
    def __init__(self, screen_size):
        self.zoom = 1.0
        self.angle = 0
        self.offset = pg.Vector2(0, 0)
        self.screen_w, self.screen_h = screen_size

    def apply(self, pos):  # pos = (x, y)
        # 카메라 오프셋 적용 + 줌 적용
        x = (pos[0] - self.offset.x) * self.zoom + self.screen_w // 2
        y = (pos[1] - self.offset.y) * self.zoom + self.screen_h // 2
        return (x, y)

    def world_to_screen(self, surf):
        # 회전 + 스케일 적용
        transformed = pg.transform.rotozoom(surf, self.angle, self.zoom)
        return transformed

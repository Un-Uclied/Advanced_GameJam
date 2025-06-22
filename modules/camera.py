import pygame as pg

class Camera2D:
    def __init__(self, screen_size=(1600, 900)):
        self.offset = pg.Vector2(0, 0)
        self.scale = 1.0
        self.screen_size = pg.Vector2(screen_size)
        self.anchor = pg.Vector2(0.5, 0.5)
    
    def reset(self):
        self.offset = pg.Vector2(0, 0)
        self.scale = 1.0
        self.anchor = pg.Vector2(0.5, 0.5)

    def world_to_screen(self, world_pos: pg.Vector2) -> pg.Vector2:
        anchor_pixel = pg.Vector2(
            self.screen_size.x * self.anchor.x,
            self.screen_size.y * self.anchor.y
        )
        return anchor_pixel + (world_pos - self.offset) * self.scale

    def screen_to_world(self, screen_pos: pg.Vector2) -> pg.Vector2:
        anchor_pixel = pg.Vector2(
            self.screen_size.x * self.anchor.x,
            self.screen_size.y * self.anchor.y
        )
        return (screen_pos - anchor_pixel) / self.scale + self.offset


    def move(self, delta: pg.Vector2):
        self.offset += delta / self.scale

    def set_zoom_from_anchor(self, new_scale: float):
        """앵커 기준으로 줌 조정"""
        new_scale = max(0.1, new_scale)
        anchor_pixel = self.screen_size.elementwise() * self.anchor

        world_before = self.screen_to_world(anchor_pixel)
        self.scale = new_scale
        world_after = self.screen_to_world(anchor_pixel)

        # 줌으로 생긴 시차 보정
        self.offset += world_before - world_after

#외부 라이브러리 임포트
import pygame as pg
from datas.const import *

class Camera2D:
    def __init__(self, scale : float, offset : pg.Vector2, anchor : pg.Vector2 = pg.Vector2(0.5, 0.5)):
        self._scale = round(scale * 2) / 2
        self.offset = offset
        self.anchor = anchor

        self.render_queue = []

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        self._scale = max(round(value * 2) / 2, 0.5)

    def world_to_screen(self, world_pos: pg.Vector2) -> pg.Vector2:
        anchor_pixel = pg.Vector2(
            SCREEN_SIZE.x * self.anchor.x,
            SCREEN_SIZE.y * self.anchor.y
        )
        return anchor_pixel + (world_pos - self.offset) * self.scale

    def screen_to_world(self, screen_pos: pg.Vector2) -> pg.Vector2:
        anchor_pixel = pg.Vector2(
            SCREEN_SIZE.x * self.anchor.x,
            SCREEN_SIZE.y * self.anchor.y
        )
        return (screen_pos - anchor_pixel) / self.scale + self.offset
    
    def get_scaled_surface(self, surface : pg.Surface, original_size : pg.Vector2 | None = None) -> pg.Surface:
        if original_size is None:
            original_size = surface.get_size()
        transform_size = (original_size[0] * self.scale, original_size[1] * self.scale)
        return pg.transform.scale(surface, transform_size)
    
    def blit(self, surface: pg.Surface, world_pos: pg.Vector2, layer: int = 0):
        self.render_queue.append((surface, world_pos, layer))

    def on_draw(self):
        from .app import App
        self.render_queue.sort(key=lambda x: x[2])  # 레이어순
        for surface, world_pos, _ in self.render_queue:
            screen_pos = self.world_to_screen(world_pos)
            scaled_surface = self.get_scaled_surface(surface)
            App.singleton.screen.blit(scaled_surface, screen_pos)
        self.render_queue.clear()

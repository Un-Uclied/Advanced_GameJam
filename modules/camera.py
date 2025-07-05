#외부 라이브러리 임포트
import pygame as pg

class Camera2D:
    screen_size = pg.Vector2(1600, 900)
    scale = 1.0
    offset = pg.Vector2(0, 0)
    anchor = pg.Vector2(0.5, 0.5)  # 화면의 중심을 기준으로 줌 조정
    
    @classmethod
    def reset(cls):
        cls.offset = pg.Vector2(0, 0)
        cls.scale = 1.0
        cls.anchor = pg.Vector2(0.5, 0.5)

    @classmethod
    def world_to_screen(cls, world_pos: pg.Vector2) -> pg.Vector2:
        anchor_pixel = pg.Vector2(
            cls.screen_size.x * cls.anchor.x,
            cls.screen_size.y * cls.anchor.y
        )
        return anchor_pixel + (world_pos - cls.offset) * cls.scale

    @classmethod
    def screen_to_world(cls, screen_pos: pg.Vector2) -> pg.Vector2:
        anchor_pixel = pg.Vector2(
            cls.screen_size.x * cls.anchor.x,
            cls.screen_size.y * cls.anchor.y
        )
        return (screen_pos - anchor_pixel) / cls.scale + cls.offset

    @classmethod
    def move(cls, delta: pg.Vector2):
        cls.offset += delta / cls.scale

    @classmethod
    def set_zoom_from_anchor(cls, new_scale: float):
        """앵커 기준으로 줌 조정"""
        new_scale = max(0.1, new_scale)
        anchor_pixel = cls.screen_size.elementwise() * cls.anchor

        world_before = cls.screen_to_world(anchor_pixel)
        cls.scale = new_scale
        world_after = cls.screen_to_world(anchor_pixel)

        # 줌으로 생긴 시차 보정
        cls.offset += world_before - world_after

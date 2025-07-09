#외부 라이브러리 임포트
import pygame as pg

class Camera2D:
    '''
    임마는 2D 카메라 클래스임
    인스턴스를 만들지 않고 클래스 메소드로 사용함
    (스태틱 클래스)
    '''
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
import pygame as pg
import math

class Component:
    def __init__(self):
        self.object = None

    def on_start(self):
        pass

    def on_destroy(self):
        pass

    def update(self):
        pass

    def draw(self):
        pass

class SpriteRenderer(Component):
    def __init__(self, image: pg.Surface, anchor: pg.Vector2 = pg.Vector2(0.5, 0.5)):
        super().__init__()
        self.image = image
        self.anchor = anchor

    def draw(self):
        if not self.image or not self.object:
            return
        
        from .core import Camera2D, GameObject

        pos = self.object.position
        rotation = self.object.rotation

        # 이미지 회전 (라디안 -> 도 변환)
        rotated_img = pg.transform.rotate(self.image, -rotation * 180 / math.pi)

        # 카메라 스케일 적용해서 이미지 크기 조절
        scale = Camera2D.scale
        new_size = rotated_img.get_width() * scale, rotated_img.get_height() * scale
        scaled_img = pg.transform.scale(rotated_img, (int(new_size[0]), int(new_size[1])))

        img_size = pg.Vector2(scaled_img.get_size())

       
        if isinstance(self.object, GameObject):
            draw_pos = Camera2D.world_to_screen(pos) - img_size.elementwise() * self.anchor
        else:
            draw_pos = pos - img_size.elementwise() * self.anchor

        from .application import Application
        surface = Application.singleton.screen

        surface.blit(scaled_img, draw_pos)

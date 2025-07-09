import pygame as pg
import math

class Component:
    '''컴포넌트 베이스 클래스'''
    def __init__(self):
        self.object = None # 컴포넌트가 속한 오브젝트를 저장하는 변수

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
        
        from .camera import Camera2D #이렇게 함수에서 임포트하면 순환참조 문제를 피할 수 있음
        from .objects import GameObject #솔직히 좀 구리긴 한데 접근성 하나만큼은 끝장남 ㅇㅇ; 성능 문제 없으니깐 됐져

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

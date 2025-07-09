import pygame as pg
import math

from .constants import *

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
        rotated_img = pg.transform.rotate(self.image, self.object.angle)  # object.angle은 도 단위로 가정

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

class Collider(Component):
    colliders = []

    def __init__(self, size: pg.Vector2, is_trigger=False):
        super().__init__()
        self.size = size
        self.is_trigger = is_trigger

    def on_start(self):
        Collider.colliders.append(self)

    def on_destroy(self):
        if self in Collider.colliders:
            Collider.colliders.remove(self)

    def get_rect(self):
        pos = self.object.position
        return pg.Rect(pos.x - self.size.x / 2, pos.y - self.size.y / 2, self.size.x, self.size.y)

    def update(self):
        my_rect = self.get_rect()
        for other in Collider.colliders:
            if other is self or not other.object:
                continue

            other_rect = other.get_rect()
            if my_rect.colliderect(other_rect):
                if not self.is_trigger and not other.is_trigger:
                    self.resolve_collision(other)
                # 트리거 콜백 호출 같은 것도 넣을 수 있음

    def resolve_collision(self, other):
        # 기본 AABB 반응
        rect1 = self.get_rect()
        rect2 = other.get_rect()

        dx = (rect2.centerx - rect1.centerx)
        dy = (rect2.centery - rect1.centery)

        overlap_x = (rect1.width + rect2.width) / 2 - abs(dx)
        overlap_y = (rect1.height + rect2.height) / 2 - abs(dy)

        if overlap_x < overlap_y:
            if dx > 0:
                self.object.position.x -= overlap_x
            else:
                self.object.position.x += overlap_x
        else:
            if dy > 0:
                self.object.position.y -= overlap_y
            else:
                self.object.position.y += overlap_y

class ObjectDebugger(Component):
    '''오브젝트 디버거 컴포넌트'''
    def __init__(self):
        super().__init__()

    def draw(self):
        if not self.object:
            return
        
        from .camera import Camera2D
        from .application import Application

        pg.draw.line(Application.singleton.screen, pg.Color(255, 0, 0), 
                     Camera2D.world_to_screen(self.object.position), 
                     Camera2D.world_to_screen(self.object.position + self.object.up * 500), 20)
        
        pg.draw.line(Application.singleton.screen, pg.Color(0, 255, 0),
                        Camera2D.world_to_screen(self.object.position), 
                        Camera2D.world_to_screen(self.object.position + self.object.right * 500), 20)
        
        if (self.object.get_component(Collider) is not None):
            collider = self.object.get_component(Collider)
            rect = collider.get_rect()
            pg.draw.rect(Application.singleton.screen, pg.Color(0, 0, 255), 
                         (Camera2D.world_to_screen(rect.topleft), pg.Vector2(rect.size) * Camera2D.scale), 2)
        
        pg.draw.circle(Application.singleton.screen, pg.Color(255, 255, 0), 
                       Camera2D.world_to_screen(self.object.position), 10)

class TextRenderer(Component):
    def __init__(self, text: str, font_size: int = 24, color: pg.Color = pg.Color(255, 255, 255), font_name = "Galmuri11.ttf"):
        super().__init__()
        self.text = text
        self.font_size = font_size
        self.color = color
        self.font = pg.freetype.Font(DEFAULT_FONT_PATH + font_name, font_size)

    def draw(self):
        if not self.object:
            return
        
        from .camera import Camera2D
        from .application import Application

        pos = Camera2D.world_to_screen(self.object.position)
        self.font.render_to(Application.singleton.screen, pos, self.text, self.color)
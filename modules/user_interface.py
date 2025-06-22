import pygame as pg
import pygame.freetype
from typing import Callable
from abc import ABC, abstractmethod

from .camera import Camera2D
# from .application import Application 점마 임포트하면 무한 임포트 가니깐 임포트 안해야함;

class UserInterface(ABC):
    @abstractmethod
    def __init__(self, app, scene):
        self.app = app
        self.scene = scene
    
    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw(self, draw_surface : pg.surface.Surface, camera : Camera2D):
        pass

class UserInterfaceManager:
    def __init__(self):
        self.world_uis = []
        self.screen_uis = []

    def clear(self):
        self.world_uis.clear()
        self.screen_uis.clear()

    def add_world_ui(self, cls, *args, **kwargs):
        new_object = cls(*args, **kwargs)
        self.world_uis.append(new_object)
        return new_object
    
    def add_screen_ui(self, cls, *args, **kwargs):
        new_object = cls(*args, **kwargs)
        self.screen_uis.append(new_object)
        return new_object

    def update(self, delta_time, events, camera):
        for world_object in self.world_uis:
            world_object.update(delta_time, events, camera)

        for camera_object in self.screen_uis:
            camera_object.update(delta_time, events, camera)

    def draw(self, main_screen : pg.surface.Surface, camera : Camera2D):
        for ui in self.world_uis:
            ui.draw(main_screen, camera)
            
        for ui in self.screen_uis:
            ui.draw(main_screen, camera)

class TextRenderer(UserInterface):
    def __init__(self, font, text, pos, fg_color="black", bg_color=None, rotation=0, size=10):
        super().__init__()
        self.font = font
        self.text = text
        self.pos = pos
        self.fg_color = fg_color
        self.bg_color = bg_color
        self.rotation = rotation
        self.size = size
        self.rect = pg.Rect(pos.x, pos.y, 0, 0)  # 기본값, draw에서 갱신될거임

    def update(self, delta_time, events, camera):
        pass
    
    def draw(self, draw_surface: pg.surface.Surface):
        scale = 1
        render_pos = self.pos

        # 텍스트 렌더링
        text_surf, text_rect = self.font.render(
            self.text,
            self.fg_color,
            self.bg_color,
            size=self.size * scale,
            rotation=self.rotation,
        )

        # 좌상단 위치로 렌더링 위치 조정
        render_rect = text_rect.move(int(render_pos.x), int(render_pos.y))
        self.rect = render_rect

        draw_surface.blit(text_surf, render_rect.topleft)

class TextButton(TextRenderer):
    def __init__(self, font, text, pos, fg_color = "black", bg_color = None, rotation = 0, size = 10):
        super().__init__(font, text, pos, fg_color, bg_color, rotation, size)

        self.registered_funcs : list[Callable] = []

    def add_listener(self, func : Callable):
        self.registered_funcs.append(func)

    def update(self, delta_time, events: list[pg.event.Event], camera: Camera2D):
        super().update(delta_time, events, camera)

        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    for func in self.registered_funcs:
                        func()


    def draw(self, target_screen, camera=None):
        super().draw(target_screen, camera)
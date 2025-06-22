import pygame as pg
import pygame.freetype
from typing import Callable
from abc import ABC, abstractmethod

from .camera import Camera2D
# from .application import Application 점마 임포트하면 무한 임포트 가니깐 임포트 안해야함;

class UserInterface(ABC):
    @abstractmethod
    def __init__(self):
        pass
    
    @abstractmethod
    def update(self, delta_time):
        pass

    @abstractmethod
    def handle_events(self, events : list[pg.event.Event]):
        pass

    @abstractmethod
    def draw(self, draw_surface : pg.surface.Surface, camera : Camera2D):
        pass

class UserInterfaceManager:
    def __init__(self, app, camera : Camera2D):
        self.app = app
        self.camera : Camera2D = camera

        self.world_uis = []
        self.screen_uis = []

    def add_world_ui(self, instance : UserInterface):
        self.world_uis.append(instance)
    
    def add_screen_ui(self, instance):
        self.screen_uis.append(instance)

    def update(self):
        for world_object in self.world_uis:
            world_object.handle_events(self.app.events)
            world_object.update(self.app.delta_time)

        for camera_object in self.screen_uis:
            camera_object.handle_events(self.app.events)
            camera_object.update(self.app.delta_time)

    def draw(self, main_screen : pg.surface.Surface):
        for world_object in self.world_uis:
            world_object.draw(main_screen, self.camera)
            
        for camera_object in self.screen_uis:
            camera_object.draw(main_screen, self.camera)

class TextRenderer(UserInterface):
    def __init__(self, font, text, pos, fg_color="black", bg_color=None, rotation=0, size=10, use_camera=False):
        super().__init__()
        self.font = font
        self.text = text
        self.pos = pos
        self.fg_color = fg_color
        self.bg_color = bg_color
        self.rotation = rotation
        self.size = size
        self.use_camera = use_camera
        self.rect = pg.Rect(pos.x, pos.y, 0, 0)  # 기본값, draw에서 갱신될거임

    def update(self, delta_time):
        pass
    
    def handle_events(self, events):
        pass

    def draw(self, draw_surface: pg.surface.Surface, camera=None):
        scale = camera.scale if self.use_camera and camera else 1

        if self.use_camera and camera:
            render_pos = camera.world_to_screen(self.pos)
        else:
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
    def __init__(self, font, text, pos, fg_color = "black", bg_color = None, rotation = 0, size = 10, use_camera = False):
        super().__init__(font, text, pos, fg_color, bg_color, rotation, size, use_camera)

        self.registered_funcs : list[Callable] = []

    def add_listener(self, func : Callable):
        self.registered_funcs.append(func)

    def update(self, delta_time):
        super().update(delta_time)

    def handle_events(self, events : list[pg.event.Event]):
        super().handle_events(events)
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    for func in self.registered_funcs:
                        func()

    def draw(self, target_screen, camera=None):
        super().draw(target_screen, camera)
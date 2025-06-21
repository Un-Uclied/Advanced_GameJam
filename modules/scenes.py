import pygame as pg
import pygame.freetype
from abc import ABC, abstractmethod

from .camera import Camera2D
from .user_interface import TextRenderer

class Scene(ABC):
    @abstractmethod
    def __init__(self, app): #여기엔 게임이 시작될때. 이미지나 다른 에
        self.app = app

    @abstractmethod
    def scene_enter(self): #플레이어나 카메라 인스턴스 만들기
        pass

    @abstractmethod
    def scene_exit(self):
        pass
        
    @abstractmethod
    def update(self, delta_time):
        pass

    @abstractmethod
    def draw(self, main_screen):
        pass

class MainMenuScene(Scene):
    def __init__(self, app):
        super().__init__(app)
    
    def scene_enter(self):
        super().scene_enter()
        self.camera : Camera2D = Camera2D()
        self.font = pygame.freetype.Font("assets/fonts/Galmuri11.ttf")
        
        self.text_render_ugui = TextRenderer(self.font, "이건 카메라 스페이스 UI", pg.Vector2(0, 0), "white", None, 0, 50, False)
        self.text_render_world = TextRenderer(self.font, "이건 월드 스페이스 UI ㅇㅇ", pg.Vector2(0, 0), "red", "yellow", 0, 50, True)

        self.moving = [False, False, False, False]
        
    def scene_exit(self):
        super().scene_exit()

    def update(self, delta_time):
        super().update(delta_time)

        events : list[pg.event.Event] = self.app.events
        for event in events:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_w:
                    self.moving[0] = True
                if event.key == pg.K_a:
                    self.moving[1] = True
                if event.key == pg.K_s:
                    self.moving[2] = True
                if event.key == pg.K_d:
                    self.moving[3] = True
            elif event.type == pg.KEYUP:
                if event.key == pg.K_w:
                    self.moving[0] = False
                if event.key == pg.K_a:
                    self.moving[1] = False
                if event.key == pg.K_s:
                    self.moving[2] = False
                if event.key == pg.K_d:
                    self.moving[3] = False
        
        self.camera.offset.y -= delta_time * 500 if self.moving[0] else 0
        self.camera.offset.x -= delta_time * 500 if self.moving[1] else 0
        self.camera.offset.y += delta_time * 500 if self.moving[2] else 0
        self.camera.offset.x += delta_time * 500 if self.moving[3] else 0



    def draw(self, main_screen : pg.surface.Surface):
        super().draw(main_screen)
        self.text_render_ugui.draw(main_screen)
        self.text_render_world.draw(main_screen, self.camera)
    
class DialogueScene(Scene):pass

class InSpaceShipScene: pass #현재 남은 일수나, 갈 행성 선택 할수 있는 ui 씬
class SpaceWarScene(Scene):pass #탑뷰형식에서 적과 전투, 탄막 피하기가 주인 씬
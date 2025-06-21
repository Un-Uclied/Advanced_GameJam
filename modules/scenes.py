import pygame as pg
import pygame.freetype
from abc import ABC, abstractmethod

from .camera import Camera2D

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
        self.font.pad = True

        self.pos = pg.Vector2(100, 200)
        self.rot = 0
        self.size = 1
        self.moving = [False, False, False, False]

    def scene_exit(self):
        super().scene_exit()

    def update(self, delta_time):
        super().update(delta_time)
        self.rot += int(delta_time)

        

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

        print(self.camera.offset)


    def draw(self, main_screen : pg.surface.Surface):
        super().draw(main_screen)
        # surf, rect = self.font.render("테스트 글!! english too.", rotation=self.rot, size=self.size, fgcolor="white")
        # rect.centerx = self.pos.x - self.camera.offset.x
        # rect.centery = self.pos.y - self.camera.offset.y
        self.font.render_to(main_screen, pg.rect.Rect(self.pos.x - self.camera.offset.x, self.pos.y - self.camera.offset.y, 0, 0), " oi oi oi 오마에와 모신데이루", "white", rotation=self.rot, size = 50)
    
class DialogueScene(Scene):pass

class InSpaceShipScene: pass #현재 남은 일수나, 갈 행성 선택 할수 있는 ui 씬
class SpaceWarScene(Scene):pass #탑뷰형식에서 적과 전투, 탄막 피하기가 주인 씬
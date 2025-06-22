import pygame as pg
import pygame.freetype
from abc import ABC, abstractmethod

from .camera import Camera2D
from .user_interface import TextRenderer, TextButton
from .user_interface import UserInterfaceManager

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
        self.camera_speed = 500
        self.font = pygame.freetype.Font("assets/fonts/Galmuri11.ttf")
        
        self.ui_manager = UserInterfaceManager(self.app, self.camera)

        self.ui_manager.add_world_ui(TextRenderer(self.font, "이건 월드 스페이스 UI ㅇㅇ", pg.Vector2(0, 0), "red", "yellow", 0, 50, True))
        self.ui_manager.add_world_ui(TextRenderer(self.font, "스키스키 다이스키", pg.Vector2(0, 200), "white", None, 0, 50, True))

        self.ui_manager.add_screen_ui(TextRenderer(self.font, "이건 카메라 스페이스 UI", pg.Vector2(0, 0), "white", None, 0, 50, False))

        button = TextButton(self.font, "이건 카메라 스페이스 버튼!!!", pg.Vector2(0, 200), "white", None, 0, 50, False)
        self.ui_manager.add_screen_ui(button)
        button.add_listener(lambda: print("클릭 된다!!"))

    def scene_exit(self):
        super().scene_exit()

    def move_camera(self, delta_time):
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            self.camera.move(pg.Vector2(0, -delta_time * self.camera_speed))
        if keys[pg.K_a]:
            self.camera.move(pg.Vector2(-delta_time * self.camera_speed, 0))
        if keys[pg.K_s]:
            self.camera.move(pg.Vector2(0, delta_time * self.camera_speed))
        if keys[pg.K_d]:
            self.camera.move(pg.Vector2(delta_time * self.camera_speed, 0))

        if keys[pg.K_q]:
            self.camera.set_zoom_from_anchor(self.camera.scale - delta_time)
        if keys[pg.K_e]:
            self.camera.set_zoom_from_anchor(self.camera.scale + delta_time)

    def update(self, delta_time):
        super().update(delta_time)
        self.move_camera(delta_time)

        self.ui_manager.update()
        
    def draw(self, main_screen : pg.surface.Surface):
        super().draw(main_screen)

        self.ui_manager.draw(main_screen)
        
        
    
class DialogueScene(Scene):pass

class InSpaceShipScene: pass #현재 남은 일수나, 갈 행성 선택 할수 있는 ui 씬
class SpaceWarScene(Scene):pass #탑뷰형식에서 적과 전투, 탄막 피하기가 주인 씬
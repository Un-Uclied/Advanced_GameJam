import pygame as pg
import pygame.freetype
from abc import ABC, abstractmethod

from .camera import Camera2D
from .user_interface import TextRenderer, TextButton, UserInterfaceManager
from .objects import ObjectManager, GameObject
from .load_image import load_sprite

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
    
    def make_entities(self):
        pass

    def make_ui(self):
        self.ui_manager.add_world_ui(TextRenderer, self.font, "이건 월드 스페이스 UI ㅇㅇ", pg.Vector2(0, 0), "red", "yellow", 0, 50)
        self.ui_manager.add_world_ui(TextRenderer, self.font, "스키스키 다이스키", pg.Vector2(0, 200), "white", None, 0, 50)

        self.ui_manager.add_screen_ui(TextRenderer, self.font, "이건 카메라 스페이스 UI", pg.Vector2(0, 0), "white", None, 0, 50)

        button = self.ui_manager.add_screen_ui(TextButton, self.font, "이건 카메라 스페이스 버튼!!!", pg.Vector2(0, 200), "white", None, 0, 50)
        button.add_listener(lambda: print("클릭 된다!!"))

        buttonWorld = self.ui_manager.add_screen_ui(TextButton, self.font, "이건 월드 스페이스 버튼!!!", pg.Vector2(0, 300), "white", "black", 0, 50)
        buttonWorld.add_listener(lambda: print("월드 클릭 이다요"))

    def make_objects(self):
        self.object_manager.add(GameObject, "statics", load_sprite())

    def scene_enter(self):
        super().scene_enter()
        self.camera : Camera2D = Camera2D()
        self.camera_speed = 500
        self.font = pygame.freetype.Font("assets/fonts/Galmuri11.ttf")
        
        self.ui_manager = UserInterfaceManager()
        self.make_ui()

        self.object_manager = ObjectManager()
        self.make_objects()

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

    def update(self):
        super().update(self.app.delta_time)
        self.move_camera(self.app.delta_time)

        self.ui_manager.update(self.app.delta_time, self.app.events, self.camera)
        self.object_manager.update(self.app.delta_time, self.app.events)
        
    def draw(self, draw_screen : pg.surface.Surface):
        super().draw(draw_screen)

        self.object_manager.draw(draw_screen, self.camera)
        self.ui_manager.draw(draw_screen, self.camera)

        pg.draw.circle(draw_screen, "blue", self.camera.world_to_screen(pg.Vector2(0, 0)), 15)
        
class DialogueScene(Scene):pass

class InSpaceShipScene: pass #현재 남은 일수나, 갈 행성 선택 할수 있는 ui 씬
class SpaceWarScene(Scene):pass #탑뷰형식에서 적과 전투, 탄막 피하기가 주인 씬
#외부 라이브러리 임포트
import pygame as pg
import pygame.freetype
from abc import ABC, abstractmethod

class Scene(ABC):
    @abstractmethod
    def __init__(self): #여기엔 게임이 시작될때. 이미지나 다른 에
        pass

    @abstractmethod
    def scene_enter(self): #플레이어나 카메라 인스턴스 만들기
        pass

    @abstractmethod
    def scene_exit(self):
        pass
        
    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw(self):
        pass

class MainMenuScene(Scene):
    font = pygame.freetype.Font("assets/fonts/Galmuri11.ttf")
    def __init__(self):
        super().__init__()

    def scene_enter(self):
        super().scene_enter()

    def scene_exit(self):
        super().scene_exit()

    def update(self):
        super().update()
        
    def draw(self):
        super().draw()
        
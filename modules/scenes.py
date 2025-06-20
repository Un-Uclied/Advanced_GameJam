import pygame as pg
from abc import ABC, abstractmethod

class Scene(ABC):
    @abstractmethod
    def __init__(self): #여기엔 게임이 시작될때. 이미지나 다른 에
        pass

    @abstractmethod
    def scene_start(self): #플레이어나 카메라 인스턴스 만들기
        pass

    @abstractmethod
    def scene_end(self):
        pass
        
    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw(self):
        pass

class MainMenuScene(Scene):pass
class DialogueScene(Scene):pass

class InSpaceShipScene: pass #현재 남은 일수나, 갈 행성 선택 할수 있는 ui 씬
class PlanetExploreScene(Scene):pass #사이드뷰 행성에서 적과 싸우거나 플랫포머하는 씬
class SpaceWarScene(Scene):pass #탑뷰형식에서 적과 전투, 탄막 피하기가 주인 씬
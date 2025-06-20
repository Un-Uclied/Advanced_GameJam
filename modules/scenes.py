from abc import ABC, abstractmethod

class Scene(ABC):
    @abstractmethod
    def __init__(self): #여기엔 게임이 시작될때. 이미지나 다른 에
        pass
    @abstractmethod
    def scene_start(self):
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

from camera import Camera
from appplication import Application

class TestScene(Scene):
    def __init__(self):
        super().__init__()
        self.app = Application()
        self.camera = Camera(self.app.screen.get_size())

    def update(self):
        super().update()
    
    def draw(self):
        super().draw()


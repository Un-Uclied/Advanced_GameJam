from abc import ABC, abstractmethod

class Scene(ABC):
    @abstractmethod
    def __init__(self):
        pass
    @abstractmethod
    def update(self):
        pass
    @abstractmethod
    def draw(self):
        pass

from render import RenderManager
from camera import Camera
from appplication import Application

class TestScene(Scene):
    def __init__(self):
        super().__init__()
        self.app = Application()
        self.camera = Camera(self.app.screen.get_size())
        self.render_manager = RenderManager()

    def update(self):
        super().update()
    
    def draw(self):
        super().draw()


#외부 라이브러리 임포트
import pygame as pg
import pygame.freetype
#내부 라이브러리 임포트
from modules.scenes import TestScene

#윈도우 설정
APPLICATION_NAME = "Game Prototype"
APPLICATION_RESOLUTION = (1600, 900)
APPLICATION_TARGET_FPS = 120

class Application:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode(APPLICATION_RESOLUTION)
        pg.display.set_caption(APPLICATION_NAME)
        self.clock = pg.time.Clock()
        self.is_running = True

        self.current_events = pg.event.get()

        self.scenes = {
            "test_scene" : TestScene()
        }
        self.current_scene = None
        self.change_scene("test_scene")
    
    def change_scene(self, scene_name : str):
        self.current_scene.scene_end()
        self.current_scene = self.scenes[scene_name]
        self.current_scene.scene_start()
    
    def run(self):
        while self.is_running:
            self.current_events = pg.event.get()
            for event in self.current_events:
                if event.type == pg.QUIT:
                    self.is_running = False
            self.current_scene.update()

            self.screen.fill((20, 20, 20))
            self.current_scene.draw()
            

            pg.display.flip()
            self.clock.tick(APPLICATION_TARGET_FPS)

        pg.quit()

if __name__ == "__main__":
    Application().run()